package com.walbrix.spring

import org.springframework.web.bind.annotation.ExceptionHandler
import org.springframework.web.bind.annotation.ResponseStatus
import java.io.FileNotFoundException
import org.springframework.http.HttpStatus
import org.springframework.web.bind.annotation.ResponseBody
import org.springframework.http.converter.HttpMessageNotReadableException
import java.io.Writer

trait RestfulErrorSupport {
	@ExceptionHandler(Array(classOf[FileNotFoundException]))
	@ResponseStatus(value = HttpStatus.NOT_FOUND)
	def notfound(ex:FileNotFoundException, writer:Writer):Unit =
	  writer.write("<html><body><h1>404 Not Found</h1>%s".format(
	      Option(ex.getCause()).map(_.getMessage()).getOrElse(ex.getMessage())
	  ))
	protected def notfound = throw new FileNotFoundException()

	@ExceptionHandler(Array(classOf[SecurityException]))
	@ResponseStatus(value = HttpStatus.FORBIDDEN)
	@ResponseBody
	def forbidden(ex:SecurityException):String = return ex.getMessage()
	protected def forbidden = throw new SecurityException()

	@ExceptionHandler(Array(classOf[HttpMessageNotReadableException]))
	@ResponseStatus(value = HttpStatus.BAD_REQUEST)
	@ResponseBody
	def httpMessageNotReadableException(ex:HttpMessageNotReadableException):String =
	  "<html><body><h1>400 Bad Request</h1>%s</body></html>".format(
	      Option(ex.getCause()).map(_.getMessage()).getOrElse(ex.getMessage())
	  )

	@ExceptionHandler(Array(classOf[IllegalArgumentException]))
	@ResponseStatus(value = HttpStatus.BAD_REQUEST)
	@ResponseBody
	def illegalArgumentException(ex:IllegalArgumentException):String =
	  "<html><body><h1>400 Bad Request</h1>%s</body></html>".format(
	      Option(ex.getCause()).map(_.getMessage()).getOrElse(ex.getMessage())
	  )
	protected def badrequest = throw new IllegalArgumentException()
}
