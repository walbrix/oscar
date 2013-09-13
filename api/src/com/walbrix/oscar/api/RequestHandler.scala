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

case class File(id:String,path:String,filename:String,atime:Timestamp,ctime:Timestamp,mtime:Timestamp,size:Long,updatedAt:Timestamp)

@Controller
@RequestMapping(Array("file"))
@Transactional
class RequestHandler extends RequestHandlerBase {
  
	implicit def long2timestamp(v:Long) = new Timestamp(v)
	
	implicit def row2file(row:Row):File =
		File(row("id"), row("path"), row("filename"), row("atime"), row("ctime"), row("mtime"), row("size"),row("updated_at"))

	@RequestMapping(value=Array(""), method = Array(RequestMethod.GET))
	@ResponseBody
	def get(@RequestParam(value="file_id_prefix",required=false) fileIdPrefix:String):Seq[(String,String,String)] = {
		(fileIdPrefix match {
		  case null => queryForSeq("select id,path from files")
		  case _ => queryForSeq("select id,path from files where id like ?", fileIdPrefix + "%") 
		}).map { row =>
			(row("id"),row("path"),row("name")):(String,String,String)
		}
	}
  
	@RequestMapping(value=Array("count"), method = Array(RequestMethod.GET))
	@ResponseBody
	def count(@RequestParam(value="path_prefix",defaultValue="/") pathPrefix:String):Tuple1[Int] = {
		Tuple1(queryForInt("select count(*) from files where path like ?", pathPrefix + "%")) 
	}

	// curl http://localhost:8080/oscar/file/ -d "path=hoge.doc" -d "atime=1000" -d "ctime=1000" -d "mtime=1000" -d "size=1024"
	@RequestMapping(value=Array(""), method = Array(RequestMethod.POST))
	@ResponseBody
	def post(path:String,name:String,atime:Long,ctime:Long,mtime:Long,size:Long):TypedResult[String] = {
		val fullPath =  path.last match  { case '/' => path + name case _ => path + "/" + name }
		update("insert into files(id,path,name,atime,ctime,mtime,size,updated_at) values(sha1(?),?,?,?,?,?,?,now()) " + 
		    "on duplicate key update atime=?,ctime=?,mtime=?,size=?,updated_at=now()",
		    fullPath, path, name, atime:Timestamp, ctime:Timestamp, mtime:Timestamp, size,
		    atime:Timestamp, ctime:Timestamp, mtime:Timestamp, size) match {
		  case 0 => false
		  case _ => TypedResult.success(queryForString("select sha1(?)", fullPath))
		}
	}
	
	@RequestMapping(value=Array("{file_id}"), method = Array(RequestMethod.DELETE))
	@ResponseBody
	def delete(@PathVariable("file_id") fileId:String):(Boolean,Option[Any]) = {
		update("delete from files where id=?", fileId) > 0
	}
	
	// curl http://localhost:8080/oscar/file/0ae8aae04779093056a501782235c73306b3238b -H "Content-Type: text/plain" -d @.mysql_history
	@RequestMapping(value=Array("{file_id}"), method = Array(RequestMethod.POST), consumes=Array("text/plain"))
	@ResponseBody
	def contents(@PathVariable("file_id") fileId:String, contents:InputStream):Result = {
		
		update("update files set contents=? where id=?", IOUtils.toString(contents, "UTF-8"), fileId) > 0
	  // http://static.springsource.org/spring/docs/3.0.x/javadoc-api/org/springframework/web/bind/annotation/RequestHeader.html
	  // http://static.springsource.org/spring/docs/current/javadoc-api/org/springframework/jdbc/core/support/SqlLobValue.html#SqlLobValue(java.io.Reader,%20int)
	}

	type FileWithSnippets = (File, String, String)
	@RequestMapping(value=Array("search"), method = Array(RequestMethod.GET))
	@ResponseBody
	def search(q:String):(Int, Seq[FileWithSnippets]) = {
		val wildq = "%" + q + "%"
		(0, queryForSeq("select * from files where path like ? or name like ? or contents like ?", wildq, wildq, wildq).map { row =>
		  	(row:File, "title snippet", "body snippet")
		})
	}
}
