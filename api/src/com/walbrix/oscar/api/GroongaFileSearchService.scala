package com.walbrix.oscar.api
import scala.collection.JavaConversions._
import org.springframework.stereotype.Component
import java.sql.Timestamp

@Component
class GroongaFileSearchService extends ServiceBase {
	implicit private def double2timestamp(v:Double) = new Timestamp((v * 1000).longValue)

	def search(q:String, offset:Int, limit:Int):(Int, Seq[FileWithSnippets]) = {
        val cmdBase = "select files --match_columns path,name,contents --output_columns \"id,path,name,atime,ctime,mtime,size,updated_at,snippet_html(path),snippet_html(name),snippet_html(contents)\" --command_version 2 --sortby _score --offset %d --limit %d --query \"".format(offset, limit)
        val json = parseJSON(queryForSingleRow("select mroonga_command(concat(?, mroonga_escape(?), '\"')) as json", cmdBase, q).headOption.map(_("json"):String).get)
        println(json)
        val results = json.get(0).iterator().drop(2).map { row =>
        	(
        		File(id=row.get(0).asText(),path=row.get(1).asText(),name=row.get(2).asText(),
        		    atime=row.get(3).asDouble(),
        		    ctime=row.get(4).asDouble(),
        		    mtime=row.get(5).asDouble(),
        		    size=row.get(6).asLong(),
        		    updatedAt=row.get(7).asDouble()),
        		row.get(8).iterator().map(_.asText).toSeq,
        		row.get(9).iterator().map(_.asText).toSeq,
        		row.get(10).iterator().map(_.asText).toSeq
        	)
        }.toSeq
        (0,results)
	}
}