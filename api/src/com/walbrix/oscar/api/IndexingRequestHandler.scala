package com.walbrix.oscar.api

import org.springframework.stereotype.Controller
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.transaction.annotation.Transactional
import java.sql.Timestamp
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.web.bind.annotation.RequestMethod
import org.springframework.web.bind.annotation.ResponseBody
import org.springframework.web.bind.annotation.RequestParam

@Controller
@RequestMapping(Array("indexing"))
@Transactional
class IndexingRequestHandler extends RequestHandlerBase {

	type IndexingRequest = (String,String, Timestamp, Option[Timestamp], Long)
	@RequestMapping(value=Array(""), method = Array(RequestMethod.GET))
	@ResponseBody
	def get():Seq[IndexingRequest] =
		queryForSeq("select * from indexing_queue where num_retry < 5 order by ifnull(updated_at,created_at)").map { row=>
		  	(row("url_id"),row("url"),row("created_at"),row("updated_at"),row("num_retry")):IndexingRequest
		}
	@RequestMapping(value=Array(""), method = Array(RequestMethod.POST))
	@ResponseBody
	def post(@RequestParam("path") path:String):TypedResult[String] = {
	  update("insert into indexing_queue(file_id,path,created_at) values(sha1(?),?,now()) on duplicate key update updated_at=now()", path, path) > 0
	}
	
	@RequestMapping(value=Array("{file_id}"), method = Array(RequestMethod.DELETE))
	@ResponseBody
	def success(@PathVariable("file_id") fileId:String):Result = {
	  update("delete from indexing_queue where file_id=?", fileId) > 0
	}

	@RequestMapping(value=Array("{file_id}/fail"), method = Array(RequestMethod.POST))
	@ResponseBody
	def fail(@PathVariable("file_id") fileId:String):Result = {
	  update("update indexing_queue set updated_at=now(),num_retry=num_retry+1 where file_id=?", fileId) > 0
	}
}
