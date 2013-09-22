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

	type IndexingRequest = (String,String,String, Timestamp, Option[Timestamp], Long)
	@RequestMapping(value=Array(""), method = Array(RequestMethod.GET))
	@ResponseBody
	def get(@RequestParam(value="limit",defaultValue="5000") limit:Int):Seq[IndexingRequest] =
		queryForSeq("select * from indexing_queue where num_retry < 5 order by num_retry,ifnull(updated_at,created_at) limit ?", limit).map { row=>
		  	(row("share_id"), row("file_id"),row("path"),row("created_at"),row("updated_at"),row("num_retry")):IndexingRequest
		}

	@RequestMapping(value=Array("recent_failed"), method = Array(RequestMethod.GET))
	@ResponseBody
	def getFailed(@RequestParam(value="limit",defaultValue="100") limit:Int):Seq[IndexingRequest] =
		queryForSeq("select * from indexing_queue where num_retry > 0 order by ifnull(updated_at,created_at) desc limit ?", limit).map { row=>
		  	(row("share_id"), row("file_id"),row("path"),row("created_at"),row("updated_at"),row("num_retry")):IndexingRequest
		}

	@RequestMapping(value=Array("{share_id}"), method = Array(RequestMethod.POST))
	@ResponseBody
	def post(@PathVariable("share_id") shareId:String,@RequestParam("path") path:String):TypedResult[String] = {
	  update("insert into indexing_queue(share_id, file_id,path,created_at) values(?, sha1(?),?,now()) on duplicate key update updated_at=now(),num_retry=0", shareId, path, path) > 0
	}
	
	@RequestMapping(value=Array("{share_id}/{file_id}"), method = Array(RequestMethod.DELETE))
	@ResponseBody
	def success(@PathVariable("share_id") shareId:String,@PathVariable("file_id") fileId:String):Result = {
	  update("delete from indexing_queue where share_id=? and file_id=?", shareId, fileId) > 0
	}
	
	@RequestMapping(value=Array("{share_id}"), method=Array(RequestMethod.DELETE))
	def deleteDir(@PathVariable("share_id") shareId:String,@RequestParam("path_prefix") pathPrefix:String):Result = {
		if (pathPrefix == "" || pathPrefix == "/") throw new IllegalArgumentException()
		update("delete from indexing_queue where share_id=? and path like ?", shareId, 
		    joinPathElements(pathPrefix, "%")) > 0
	}


	@RequestMapping(value=Array("{share_id}/{file_id}/fail"), method = Array(RequestMethod.POST))
	@ResponseBody
	def fail(@PathVariable("share_id") shareId:String,@PathVariable("file_id") fileId:String):Result = {
	  update("update indexing_queue set updated_at=now(),num_retry=num_retry+1 where share_id=? and file_id=?", shareId, fileId) > 0
	}
}
