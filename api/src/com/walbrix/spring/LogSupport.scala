package com.walbrix.spring

import org.apache.commons.logging.LogFactory

trait LogSupport extends org.springframework.web.context.ServletContextAware {
	self =>
	private val logger = org.apache.commons.logging.LogFactory.getLog(self.getClass());
	private var _jetty:Boolean = false
	
	def log = logger
	
	override def setServletContext(servletContext:javax.servlet.ServletContext):Unit = {
		_jetty = servletContext.getServerInfo().startsWith("jetty")
	}
	
	protected def debug(arg:Any) = {
		if (_jetty) {
		  logger.info(arg)
		} else {
		  logger.debug(arg)
		}
	}
}
