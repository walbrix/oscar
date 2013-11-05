package com.walbrix.oscar.api

import org.junit.runner.RunWith
import org.springframework.test.context.ContextConfiguration
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner
import org.springframework.test.context.ActiveProfiles
import org.springframework.transaction.annotation.Transactional
import org.springframework.beans.factory.annotation.Autowired
import org.junit.Test

@RunWith(classOf[SpringJUnit4ClassRunner])
@ContextConfiguration(locations=Array("classpath:beans.xml"))
@ActiveProfiles(Array("dev"))
@Transactional
class AdRequestHandlerTest {
	@Autowired private var requestHandler:AdRequestHandler = _
	@Test def testGet() = {
	  println(requestHandler.get("ad728x90-bs3"))
	}
}