package com.walbrix.jackson

import scala.collection.JavaConversions._
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.Module
import com.fasterxml.jackson.core.JsonParser.Feature
import com.fasterxml.jackson.databind.PropertyNamingStrategy.LowerCaseWithUnderscoresStrategy

class SpringFriendlyJacksonObjectMapper extends ObjectMapper {
  
	this.configure(Feature.ALLOW_COMMENTS, true);
	this.configure(Feature.ALLOW_UNQUOTED_FIELD_NAMES, true);
  
	def setModules(modules:java.util.List[Module]) = {
		for (module <- modules) {
			this.registerModule(module);
		}
	}
}
