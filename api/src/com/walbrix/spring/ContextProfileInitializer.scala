package com.walbrix.spring;

import org.springframework.context.ApplicationContextInitializer;
import org.springframework.web.context.ConfigurableWebApplicationContext;

class ContextProfileInitializer extends AnyRef
	with ApplicationContextInitializer[ConfigurableWebApplicationContext] {

	override def initialize(ctx:ConfigurableWebApplicationContext) = 
		ctx.getEnvironment().setActiveProfiles(
		    Map(true->"dev",false->"prod")(ctx.getServletContext().getServerInfo().startsWith("jetty"))
		)
}
