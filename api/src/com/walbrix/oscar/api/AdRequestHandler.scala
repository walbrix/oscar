package com.walbrix.oscar.api

import org.springframework.stereotype.Controller
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.transaction.annotation.Transactional
import org.springframework.web.bind.annotation.RequestMethod
import org.springframework.web.bind.annotation.ResponseBody
import org.springframework.web.bind.annotation.PathVariable

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
  
	@RequestMapping(value=Array("{size}"), method = Array(RequestMethod.GET))
	@ResponseBody
	def get(@PathVariable("size") size:String):Tuple1[String] = {
	  if (size.indexOf("x") < 0) throw new IllegalArgumentException()
	  val wh = size.split("x").map(Integer.parseInt(_))
	  val (width, height) = (wh(0),wh(1))
	  if (isLicensed) {
	    Tuple1("")
	  } else {
	    Tuple1("<iframe scrolling=\"no\" src=\"http://va.walbrix.net/ad/ad%s.html\" width=\"%d\" height=\"%d\" seamless=\"\"></iframe>".format(size,width,height))
	  }
	}

}