package com.walbrix.oscar.api

import org.springframework.stereotype.Controller
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.transaction.annotation.Transactional
import org.springframework.web.bind.annotation.RequestMethod
import org.springframework.web.bind.annotation.ResponseBody
import org.springframework.web.bind.annotation.RequestParam

case class File()

@Controller
@RequestMapping(Array("file"))
@Transactional
class RequestHandler extends RequestHandlerBase {

	@RequestMapping(value=Array(""), method = Array(RequestMethod.GET))
	@ResponseBody
	def get(@RequestParam(value="file_id_prefix",required=false) fileIdPrefix:String):Seq[String] = {
	  Seq()
	}
  
	@RequestMapping(value=Array(""), method = Array(RequestMethod.POST))
	@ResponseBody
	def post(path:String,atime:Long,ctime:Long,mtime:Long):(Boolean,Option[String]) = {
	  (false, None)
	}
	
	@RequestMapping(value=Array("{file_id}"), method = Array(RequestMethod.DELETE))
	@ResponseBody
	def delete(fileId:String):(Boolean,Option[Any]) = {
	  (false, None)
	}
	
	@RequestMapping(value=Array("{file_id}"), method = Array(RequestMethod.POST), consumes=Array("text/plain"))
	@ResponseBody
	def contents(fileId:String, reader:java.io.Reader):(Boolean, Option[Any]) = {
	  // http://static.springsource.org/spring/docs/3.0.x/javadoc-api/org/springframework/web/bind/annotation/RequestHeader.html
	  // http://static.springsource.org/spring/docs/current/javadoc-api/org/springframework/jdbc/core/support/SqlLobValue.html#SqlLobValue(java.io.Reader,%20int)
	  (false, None)
	}
	
	@RequestMapping(value=Array("search"), method = Array(RequestMethod.GET))
	@ResponseBody
	def search(q:String):Seq[File] = {
	  Seq()
	}
}
