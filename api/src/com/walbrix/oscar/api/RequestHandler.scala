package com.walbrix.oscar.api

import org.springframework.stereotype.Controller
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.transaction.annotation.Transactional
import org.springframework.web.bind.annotation.RequestMethod
import org.springframework.web.bind.annotation.ResponseBody
import org.springframework.web.bind.annotation.RequestParam
import java.sql.Timestamp
import com.walbrix.spring.Row
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.jdbc.core.support.SqlLobValue
import org.springframework.web.bind.annotation.RequestHeader
import org.springframework.web.bind.annotation.RequestBody
import java.io.InputStream
import org.apache.commons.io.IOUtils
import org.springframework.beans.factory.annotation.Autowired

case class File(id:String,path:String,name:String,atime:Timestamp,ctime:Timestamp,mtime:Timestamp,size:Long,updatedAt:Timestamp)

@Controller
@RequestMapping(Array("file"))
@Transactional
class RequestHandler extends RequestHandlerBase {
  	@Autowired private var searchService:GroongaFileSearchService = _

	implicit def long2timestamp(v:Long) = new Timestamp(v)
	
	implicit def row2file(row:Row):File =
		File(row("id"), row("path"), row("name"), row("atime"), row("ctime"), row("mtime"), row("size"),row("updated_at"))

	// <4096 == ""
	// <65536 == "0"
	// <1048576 == "00"
	// <16777216 == "000"
	// <268435456 == "0000"
	@RequestMapping(value=Array("{share_id}"), method = Array(RequestMethod.GET))
	@ResponseBody
	def get(@PathVariable("share_id") shareId:String, @RequestParam(value="file_id_prefix",required=false) fileIdPrefix:String):Seq[(String,String,String)] = {
		(fileIdPrefix match {
		  case null => queryForSeq("select id,path from files where share_id=?", shareId)
		  case _ => queryForSeq("select id,path from files where share_id=? and id like ?", shareId, fileIdPrefix + "%") 
		}).map { row =>
			(row("id"),row("path"),row("name")):(String,String,String)
		}
	}
  
	@RequestMapping(value=Array("{share_id}/count"), method = Array(RequestMethod.GET))
	@ResponseBody
	def count(@PathVariable("share_id") shareId:String,@RequestParam(value="path_prefix",defaultValue="/") pathPrefix:String):Tuple1[Long] = {
		Tuple1(queryForLong("select count(*) from files where share_id=? and path=? or path like concat(?, '/%')", shareId, pathPrefix, pathPrefix)) 
	}

	// curl http://localhost:8080/oscar/file/ -d "path=hoge.doc" -d "atime=1000" -d "ctime=1000" -d "mtime=1000" -d "size=1024"
	@RequestMapping(value=Array("{share_id}"), method = Array(RequestMethod.POST))
	@ResponseBody
	def post(@PathVariable("share_id") shareId:String,path:String,name:String,atime:Long,ctime:Long,mtime:Long,size:Long):TypedResult[String] = {
		val fullPath =  path.last match  { case '/' => path + name case _ => path + "/" + name }
		update("insert into files(share_id,id,path,name,atime,ctime,mtime,size,updated_at) values(?,sha1(?),?,?,?,?,?,?,now()) " + 
		    "on duplicate key update atime=?,ctime=?,mtime=?,size=?,updated_at=now()",
		    shareId, fullPath, path, name, atime:Timestamp, ctime:Timestamp, mtime:Timestamp, size,
		    atime:Timestamp, ctime:Timestamp, mtime:Timestamp, size) match {
		  case 0 => false
		  case _ => TypedResult.success(queryForString("select sha1(?)", fullPath))
		}
	}
	
	@RequestMapping(value=Array("{share_id}/{file_id}"), method = Array(RequestMethod.DELETE))
	@ResponseBody
	def delete(@PathVariable("share_id") shareId:String,@PathVariable("file_id") fileId:String):(Boolean,Option[Any]) = {
		update("delete from files where share_id=? and id=?", shareId, fileId) > 0
	}
	
	@RequestMapping(value=Array("{share_id}/delete_by_path_prefix"), method=Array(RequestMethod.POST))
	def deleteDir(@PathVariable("share_id") shareId:String,@RequestParam("path_prefix") pathPrefix:String):Result = {
		if (pathPrefix == "" || pathPrefix == "/") throw new IllegalArgumentException()
		update("delete from files where share_id=? and (path=? or path like concat(?, '/%'))", shareId, pathPrefix, pathPrefix) > 0
	}
	
	// curl http://localhost:8080/oscar/file/0ae8aae04779093056a501782235c73306b3238b -H "Content-Type: text/plain" -d @.mysql_history
	@RequestMapping(value=Array("{share_id}/{file_id}"), method = Array(RequestMethod.POST), consumes=Array("text/plain"))
	@ResponseBody
	def contents(@PathVariable("share_id") shareId:String,@PathVariable("file_id") fileId:String, contents:InputStream):Result = {
		
		update("update files set contents=? where share_id=? and id=?", IOUtils.toString(contents, "UTF-8"), shareId, fileId) > 0
	  // http://static.springsource.org/spring/docs/3.0.x/javadoc-api/org/springframework/web/bind/annotation/RequestHeader.html
	  // http://static.springsource.org/spring/docs/current/javadoc-api/org/springframework/jdbc/core/support/SqlLobValue.html#SqlLobValue(java.io.Reader,%20int)
	}
	
	@RequestMapping(value=Array("{share_id}/recent"), method = Array(RequestMethod.GET))
	@ResponseBody
	def recent(@RequestParam(value="path_prefix",defaultValue="/") pathPrefix:String,
	    @RequestParam(value="offset",defaultValue="0") offset:Int,
	    @RequestParam(value="limit",defaultValue="10") limit:Int):Seq[File] = {
		queryForSeq("select id,path,name,atime,ctime,mtime,size,updated_at from files where " + 
		    "path=? or path like concat(?, '/%') " + 
		    "order by mtime desc limit ?,?", pathPrefix, pathPrefix, offset, limit).map { row =>
		  	row:File
		}
	}

	@RequestMapping(value=Array("{share_id}/search"), method = Array(RequestMethod.GET))
	@ResponseBody
	def search(@PathVariable("share_id") shareId:String,
	    @RequestParam("q") q:String, @RequestParam(value="path_prefix",defaultValue="/") pathPrefix:String,
	    @RequestParam(value="offset",defaultValue="0") offset:Int,
	    @RequestParam(value="limit",defaultValue="10") limit:Int):(Int, Seq[FileWithSnippets]) = {
		searchService.search(shareId, pathPrefix, q, offset, limit)
		/*
		val wildq = "%" + q + "%"
		(0, queryForSeq("select * from files where path like ? or name like ? or contents like ?", wildq, wildq, wildq).map { row =>
		  	(row:File, "title snippet", "body snippet")
		})*/
	}
}
