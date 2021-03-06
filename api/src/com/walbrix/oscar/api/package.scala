package com.walbrix.oscar

import java.io.InputStream
import com.fasterxml.jackson.databind.JsonNode
package object api {
	// util
	private val objectMapper = new com.fasterxml.jackson.databind.ObjectMapper() // supposed to be thread safe
	def loadJSON(is:InputStream):JsonNode = objectMapper.readTree(is)
	def parseJSON(s:String):JsonNode = objectMapper.readTree(s)
  
	// Base Service class
	trait ServiceBase extends AnyRef
		with com.walbrix.spring.DataSourceSupport 
		with com.walbrix.spring.LogSupport
	// Base Request Handler class
	trait RequestHandlerBase extends ServiceBase
		with com.walbrix.spring.RestfulErrorSupport

	// types
	type FileWithSnippets = (File, Seq[String], Seq[String], Seq[String])

	// Result types
	type TypedResult[T] = (Boolean, Option[T])

	object TypedResult {
		def apply[T](success:Boolean):TypedResult[T] = (success, None)
		def apply[T](success:Boolean, value:T):TypedResult[T] = (success, Some(value))
		def success[T](value:T):TypedResult[T] = TypedResult(true, value)
		def success[T]():TypedResult[T] = TypedResult(true)
		def fail[T]():TypedResult[T] = TypedResult(false)
	}
	
	type Result = TypedResult[Any]

	object Result {
		def apply(success:Boolean):Result = (success, None)
		def apply(success:Boolean, value:Any):Result = (success, Some(value))
		def success(value:Any):Result = Result(true, value)
		def success():Result = Result(true)
		def fail(value:Any):Result = Result(false, value)
		def fail():Result = Result(false)
	}
	
	implicit def result2boolean[T](result:TypedResult[T]) = result._1
	implicit def boolean2result[T](bool:Boolean) = TypedResult[T](bool)

	// utils
	def joinPathElements(a:String,b:String):String = {
  		if (a.endsWith("/") && b.startsWith("/")) return a + b.substring(1)
  		if (!a.endsWith("/") && !b.startsWith("/")) return a + "/" + b
  		return a + b
  	}
}