<?php
//
// +----------------------------------------------------------------------+
// |zen-cart Open Source E-commerce                                       |
// +----------------------------------------------------------------------+
// | Copyright (c) 2003 The zen-cart developers                           |
// |                                                                      |   
// | http://www.zen-cart.com/index.php                                    |   
// |                                                                      |   
// | Portions Copyright (c) 2003 osCommerce                               |
// +----------------------------------------------------------------------+
// | This source file is subject to version 2.0 of the GPL license,       |
// | that is bundled with this package in the file LICENSE, and is        |
// | available through the world-wide-web at the following url:           |
// | http://www.zen-cart.com/license/2_0.txt.                             |
// | If you did not receive a copy of the zen-cart license and are unable |
// | to obtain it through the world-wide-web, please send a note to       |
// | license@zen-cart.com so we can mail you a copy immediately.          |
// +----------------------------------------------------------------------+
// $Id: joecoin.php itwaslikethiswhenifoundit $ Modifications for Scorebot CTF system, renamed joecoin.php 2017-05-31
// 
// modified from:
// DIRBANKUSA.php 1106 2009-11-24 22:05:35Z CRYSTAL JONES $ modify from Auzbank of OZcommerce module by birdbrain
//

if(!defined('EOL')){
	define('EOL', "\r\n");
}


  class joecoin {
    var $code, $title, $description, $enabled;


// class constructor
    function joecoin() {
      global $order;

      $this->code = 'joecoin';
      $this->title = MODULE_PAYMENT_JOECOIN_TEXT_TITLE;
      $this->description = MODULE_PAYMENT_JOECOIN_TEXT_DESCRIPTION;
      $this->email_footer = MODULE_PAYMENT_JOECOIN_TEXT_EMAIL_FOOTER;
      $this->sort_order = MODULE_PAYMENT_JOECOIN_SORT_ORDER;
      $this->enabled = ((MODULE_PAYMENT_JOECOIN_STATUS == 'True') ? true : false);

      if ((int)MODULE_PAYMENT_JOECOIN_ORDER_STATUS_ID > 0) {
        $this->order_status = MODULE_PAYMENT_JOECOIN_ORDER_STATUS_ID;
      }

      if (is_object($order)) $this->update_status();
    }

// class methods (joecoin-specific)
	private function exchange_rate_api_query($team = null){
		
		// error_log(__FUNCTION__."() - session contents:\n\n\ ".print_r($_SESSION, true)."\n\n");
		
		if(is_null($team)){
			$team = $_SESSION['customer_id'];
		}
		
		$request =  'GET '.MODULE_PAYMENT_JOECOIN_PATH.'/'.$team.' HTTP/1.1'.EOL.
					'Host: '.MODULE_PAYMENT_JOECOIN_APIHOST.EOL.
					'SBE-AUTH: '.MODULE_PAYMENT_JOECOIN_APIKEY.EOL.
					'Accept-Encoding: gzip, deflate'.EOL.
					'Accept: */*'.EOL.
					EOL;
		
		$http = fsockopen('tcp://'.MODULE_PAYMENT_JOECOIN_APIHOST.':'.MODULE_PAYMENT_JOECOIN_APIPORT);
		if(!$http){
			error_log(__CLASS__.'::'.__FUNCTION__.'() - Failed to open HTTP socket on '
					.MODULE_PAYMENT_JOECOIN_APIHOST.' for POST to '.MODULE_PAYMENT_JOECOIN_PATH);
			
			return false;
		}
		error_log(__CLASS__.'::'.__FUNCTION__."() - socket opened. Request prepared:\n\n{$request}");
		
		fwrite($http, $request, strlen($request));
		
		$resp = "";
		while (!feof($http)) {
			$resp .= fgets($http, 128);
		}
		fclose($http);
		
		error_log(__CLASS__.'::'.__FUNCTION__."() - SBE joecoin exchange rate response:\n\n".EOL.$resp);
		
		// Extract status code
		if(false !== preg_match('#HTTP/1.1\s(?<status>\d+)#', $resp, $m) && $m['status'] == '200'){
			 // Extract conversion factor
			 $lines = explode(EOL, $resp);
			 $body = json_decode( $lines[count($lines)-1] );
			 return $body->rate;
		}else{ // or explicitly fail
			error_log(__CLASS__.'::'.__FUNCTION__."() - Could not extract exchange rate, HTTP response code {$m['status']}");
			return false;
		}
	}
    
    private function purchase_api_call($team, $order = array('item' => "no product names provided", 'price' => 0)) {
		$fields = array(
			'team' => $team,
			'order' => $order,
		);
		$fields = json_encode($fields, true);
		$request =  'POST '.MODULE_PAYMENT_JOECOIN_PATH.' HTTP/1.1'.EOL.
					'Host: '.MODULE_PAYMENT_JOECOIN_APIHOST.EOL.
					'SBE-AUTH: '.MODULE_PAYMENT_JOECOIN_APIKEY.EOL.
					'Accept-Encoding: gzip, deflate'.EOL.
					'Accept: */*'.EOL.
					'Content-Length: '.strlen($fields).EOL.
					EOL.
					$fields.EOL.
					EOL;
		
					
		error_log(__FUNCTION__.'():  request - '."\n\n".print_r($request,true)."\n\n");
		
		$http = fsockopen('tcp://'.MODULE_PAYMENT_JOECOIN_APIHOST.':'.MODULE_PAYMENT_JOECOIN_APIPORT);
		if(!$http){
			error_log(__CLASS__.'::'.__FUNCTION__.' - Failed to open HTTP socket on '.MODULE_PAYMENT_JOECOIN_APIHOST.' for POST to '.MODULE_PAYMENT_JOECOIN_PATH);
			return false;
		}
		fwrite($http, $request, strlen($request));
		
		$resp = "";
		while (!feof($http)) {
			$resp .= fgets($http, 128);
		}
		fclose($http);
		
		error_log("SBE Purchase transaction response: ".EOL.$resp);
		 
		// Extract status code
		if(false !== preg_match('#HTTP/1.1\s(?<status>\d+)#', $resp, $m)){
			return $m['status'];
		}else{ // or explicitly fail
			error_log("Could not extract HTTP response code!");
			return false;
		}
    }
      


// class methods (framework-defined, general)
    function update_status() {
      global $order, $db;

      if ( ($this->enabled == true) && ((int)MODULE_PAYMENT_JOECOIN_ZONE > 0) ) {
        $check_flag = false;
        $check = $db->Execute("select zone_id from " . TABLE_ZONES_TO_GEO_ZONES . " where geo_zone_id = '" . MODULE_PAYMENT_JOECOIN_ZONE . "' and zone_country_id = '" . $order->delivery['country']['id'] . "' order by zone_id");
        while (!$check->EOF) {
          if ($check->fields['zone_id'] < 1) {
            $check_flag = true;
            break;
          } elseif ($check->fields['zone_id'] == $order->delivery['zone_id']) {
            $check_flag = true;
            break;
          }
          $check->MoveNext();
        }

        if ($check_flag == false) {
          $this->enabled = false;
        }
      }
    }

    function javascript_validation() {
      return false;
    }

    function selection() {
      return array('id' => $this->code,
                   'module' => $this->title);
    }

    function pre_confirmation_check() {
      return false;
    }

    function confirmation() { // Fetch and display Joecoin/points estimate here
    	
    	// Global variables: just getting $%#! done since 1962
    	global $order;
    	
    	$joecoinTotal = 0;
    	foreach( $order->products as $i => $prod){
    		$joecoinTotal += $prod['qty'] * $prod['price'];    		
    	}
    	
    	if($exchangeRate = $this->exchange_rate_api_query()){
    		$pointsTotal = $joecoinTotal * $exchangeRate;
    		error_log("Purchase for {$joecoinTotal} Joecoin estimated to consume {$pointsTotal} scoreboard points at ".time());
    		$pointsTotalMsg = '<i>This purchase is expected to cost a total of <b>'
    							.number_format($pointsTotal)
    							.'</b> game points. Please make a note of it.</i>';
    		
    	}else{
    		$pointsTotalMsg = "Error retrieving exchange rate for cart-screen points cost estimate!";
    		error_log($pointsTotalMsg);
    	}
    	
      return array( 'title' => $pointsTotalMsg );
    }

    function before_process() {
      return false;
    }

    function process_button() {  

    }

    function after_process() {  // enact transaction. The die is cast. 
    	global $order;
    	
    	$orderItems = array();
    	foreach( $order->products as $i => $prod){
    		for($j=0; $j<$prod['qty']; $j++){
    			$orderItems[] = array( 'item' => $prod['name'],
    					'price' => $prod['price'] );
    		}
    	}
    	
    	$team = is_null($order->customer['name']) ? $_SESSION['customer_id'] : $order->customer['name'];
    	
    	if($status = $this->purchase_api_call($team, $orderItems)){
    		return MODULE_PAYMENT_JOECOIN_TEXT_DESCRIPTION;
    		return array('title' => MODULE_PAYMENT_JOECOIN_TEXT_DESCRIPTION);
    	}else{
    		return 'ERROR!  '.$status;
    		return array('title' => 'ERROR!  '.$status);
    	}
      return false;
    }

    function get_error() {
      return false;
    }

    function check() {
      global $db;
      if (!isset($this->_check)) {
        $check_query = $db->Execute("select configuration_value from " . TABLE_CONFIGURATION . " where configuration_key = 'MODULE_PAYMENT_JOECOIN_STATUS'");
        $this->_check = $check_query->RecordCount();
      }
      return $this->_check;
    }

    function install() {
      global $db;
     $db->Execute("insert into " . TABLE_CONFIGURATION . " (configuration_title, configuration_key, configuration_value, configuration_description, configuration_group_id, sort_order, set_function, date_added) values ('Enable Joecoin Module', 'MODULE_PAYMENT_JOECOIN_STATUS', 'True', 'Do you want to accept Joecoin payments?', '6', '1', 'zen_cfg_select_option(array(\'True\', \'False\'), ', now())");
	 $db->Execute("insert into " . TABLE_CONFIGURATION . " (configuration_title, configuration_key, configuration_value, configuration_description, configuration_group_id, sort_order, use_function, set_function, date_added) values ('Payment Zone', 'MODULE_PAYMENT_JOECOIN_ZONE', '0', 'If a zone is selected, only enable this payment method for that zone.', '6', '2', 'zen_get_zone_class_title', 'zen_cfg_pull_down_zone_classes(', now())");
     $db->Execute("insert into " . TABLE_CONFIGURATION . " (configuration_title, configuration_key, configuration_value, configuration_description, configuration_group_id, sort_order, date_added) values ('Sort order of display.', 'MODULE_PAYMENT_JOECOIN_SORT_ORDER', '0', 'Sort order of display. Lowest is displayed first.', '6', '0', now())");
     $db->Execute("insert into " . TABLE_CONFIGURATION . " (configuration_title, configuration_key, configuration_value, configuration_description, configuration_group_id, sort_order, date_added) values ('SBE API Key', 'MODULE_PAYMENT_JOECOIN_APIKEY', 'password', 'SBE API Key', '6', '1', now());");
     $db->Execute("insert into " . TABLE_CONFIGURATION . " (configuration_title, configuration_key, configuration_value, configuration_description, configuration_group_id, sort_order, date_added) values ('SBE Purchase API host', 'MODULE_PAYMENT_JOECOIN_APIHOST', '10.x.y.z', 'SBE API host', '6', '1', now());");
     $db->Execute("insert into " . TABLE_CONFIGURATION . " (configuration_title, configuration_key, configuration_value, configuration_description, configuration_group_id, sort_order, date_added) values ('SBE Purchase API port', 'MODULE_PAYMENT_JOECOIN_APIPORT', '8080', 'SBE API port', '6', '1', now());");
     $db->Execute("insert into " . TABLE_CONFIGURATION . " (configuration_title, configuration_key, configuration_value, configuration_description, configuration_group_id, sort_order, date_added) values ('Endpoint path', 'MODULE_PAYMENT_JOECOIN_PATH', '/api/purchase', 'Purchase endpoint path', '6', '1', now());");
     $db->Execute("insert into " . TABLE_CONFIGURATION . " (configuration_title, configuration_key, configuration_value, configuration_description, configuration_group_id, sort_order, set_function, use_function, date_added) values ('Set Order Status', 'MODULE_PAYMENT_JOECOIN_ORDER_STATUS_ID', '0', 'Set the status of orders made with this payment module to this value', '6', '0', 'zen_cfg_pull_down_order_statuses(', 'zen_get_order_status_name', now())");
   }

    function remove() {
      global $db;
      $db->Execute("delete from " . TABLE_CONFIGURATION . " where configuration_key in ('" . implode("', '", $this->keys()) . "')");
    }

    function keys() {
    	return array('MODULE_PAYMENT_JOECOIN_STATUS', 'MODULE_PAYMENT_JOECOIN_ZONE', 'MODULE_PAYMENT_JOECOIN_SORT_ORDER', 'MODULE_PAYMENT_JOECOIN_APIKEY', 'MODULE_PAYMENT_JOECOIN_APIHOST',  'MODULE_PAYMENT_JOECOIN_PATH', 'MODULE_PAYMENT_JOECOIN_ORDER_STATUS_ID', 'MODULE_PAYMENT_JOECOIN_APIPORT');
    }
  }
?>
