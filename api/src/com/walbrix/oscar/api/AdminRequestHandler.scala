package com.walbrix.oscar.api

import org.springframework.stereotype.Controller
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.transaction.annotation.Transactional
import org.springframework.web.bind.annotation.RequestMethod
import org.springframework.web.bind.annotation.ResponseBody
import java.sql.SQLException

@Controller
@RequestMapping(Array("admin"))
@Transactional
class AdminRequestHandler extends RequestHandlerBase {
	@RequestMapping(value=Array("RESET"), method=Array(RequestMethod.POST))
	@ResponseBody
	def reset():Result = {
		try {
			execute("flush tables")
		}
		catch {
		  case ex:SQLException => ;
		}
		execute("truncate table files")
		execute("truncate table indexing_queue")
		execute("flush tables")
		true
  	}

	@RequestMapping(value=Array("FLUSH"), method = Array(RequestMethod.POST))
	@ResponseBody
	def flush():Result = {
		execute("flush tables")
		true
	}
}