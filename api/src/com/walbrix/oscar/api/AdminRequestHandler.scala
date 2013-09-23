package com.walbrix.oscar.api

import org.springframework.stereotype.Controller
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.transaction.annotation.Transactional
import org.springframework.web.bind.annotation.RequestMethod
import org.springframework.web.bind.annotation.ResponseBody

@Controller
@RequestMapping(Array("admin"))
@Transactional
class AdminRequestHandler extends RequestHandlerBase {
	@RequestMapping(value=Array("RESET"), method=Array(RequestMethod.POST))
	@ResponseBody
	def reset():Result = {
		execute("truncate table files")
		execute("truncate table indexing_queue")
		true
  	}
}