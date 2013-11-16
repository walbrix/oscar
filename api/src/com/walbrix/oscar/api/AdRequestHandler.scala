package com.walbrix.oscar.api

import org.springframework.stereotype.Controller
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.transaction.annotation.Transactional
import org.springframework.web.bind.annotation.RequestMethod
import org.springframework.web.bind.annotation.ResponseBody
import org.springframework.web.bind.annotation.PathVariable
import java.net.URL
import org.apache.commons.io.IOUtils

@Controller
@RequestMapping(Array("ad"))
@Transactional
class AdRequestHandler extends RequestHandlerBase {
  
	private def isLicensed():Boolean = {
		(queryForSingleRow("select value from system_settings where name='licensed'").getOrElse(return false)("value"):String) match {
		  case "true"|"True"|"TRUE"|"yes"|"Yes"|"YES"|"1" => true
		  case _ => false
		}
	}
  
	@RequestMapping(value=Array("{name}"), method = Array(RequestMethod.GET))
	@ResponseBody
	def get(@PathVariable("name") name:String):Tuple1[String] = {
	  if (isLicensed) {
	    Tuple1("")
	  } else {
	    val is = new URL("http://ad.walbrix.com/oscar/%s.html".format(name)).openStream()
	    try{
	    	Tuple1(IOUtils.toString(is))
	    }
	    finally {
	    	is.close()
	    }
	  }
	}

}