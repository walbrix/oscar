package com.walbrix.oscar.api
import scala.collection.JavaConversions._
import org.springframework.stereotype.Component
import java.sql.Timestamp

@Component
class GroongaFileSearchService extends ServiceBase {
	implicit private def double2timestamp(v:Double) = new Timestamp((v * 1000).longValue)

	def search(shareId:String, pathPrefix:String, q:String, offset:Int, limit:Int):(Int, Seq[FileWithSnippets]) = {
		val (escapedShareId,escapedPath, escapedQuery) = 
		  queryForSingleRow("select mroonga_escape(?) as share_id,mroonga_escape(?) as path,mroonga_escape(?) as query", shareId, pathPrefix, q).map { row =>
		  	(row("share_id"), row("path"), row("query")):(String,String,String)
		}.get
        val cmd = ("select files --match_columns path||name*10||contents*5 " +
          "--output_columns 'id,path,name,atime,ctime,mtime,size,sha1sum,updated_at,snippet_html(path),snippet_html(name),snippet_html(contents)' " + 
          "--command_version 2 --sortby -_score --offset %d --limit %d " +
          "--filter 'share_id == \"%s\" && (path == \"%s\"|| path @^ \"%s\")' " +
          "--query '%s'").format(offset, limit, escapedShareId, escapedPath, joinPathElements(escapedPath, ""), escapedQuery)
        println(cmd)
        val json = parseJSON(queryForSingleRow("select mroonga_command(?) as json", cmd).headOption.map(_("json"):String).get)
        println(json)
        val results = json.get(0).iterator().drop(2).map { row =>
        	(
        		File(id=row.get(0).asText(),path=row.get(1).asText(),name=row.get(2).asText(),
        		    atime=row.get(3).asDouble(),
        		    ctime=row.get(4).asDouble(),
        		    mtime=row.get(5).asDouble(),
        		    size=row.get(6).asLong(),
        		    sha1sum=row.get(7).asText(),
        		    updatedAt=row.get(8).asDouble()),
        		row.get(9).iterator().map(_.asText).toSeq,
        		row.get(10).iterator().map(_.asText).toSeq,
        		row.get(11).iterator().map(_.asText).toSeq
        	)
        }.toSeq
        (json.get(0).get(0).get(0).asInt(),results)
	}
}