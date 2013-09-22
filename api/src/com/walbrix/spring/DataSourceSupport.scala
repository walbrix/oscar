package com.walbrix.spring

import java.math.BigInteger
import java.sql.Timestamp
import javax.sql.DataSource
import scala.collection.JavaConversions._
import org.springframework.beans.factory.annotation.Autowired

class Row protected(row:java.util.Map[String,AnyRef]) {
	private val this.row = row

	type DI = DummyImplicit
  
	def getColumn(col:String):AnyRef = {
	    assert(row.containsKey(col))
	    row.get(col)
	}

	def int(col:String):Int = {
		getColumn(col) match {
			case null => 0
			case x:Number => x.asInstanceOf[Number].intValue()
			case y:String => y.toInt
		}
	}

	def int(col:String)(implicit d1:DI):Option[Int] = {
	  getColumn(col) match {
	      case null => None
	      case x:Number => Some(x.asInstanceOf[Number].intValue())
	      case y:String => Some(y.toInt)
	  }
	}

    def short(col:String):Short = {
	  getColumn(col) match {
	      case null => 0
	      case x:Number => x.asInstanceOf[Number].shortValue()
	      case y:String => y.toShort
	  }
	}

	def short(col:String)(implicit d1:DI):Option[Short] = {
	  getColumn(col) match {
	      case null => None
	      case x:Number => Some(x.asInstanceOf[Number].shortValue())
	      case y:String => Some(y.toShort)
	  }
	}

	def apply(col:String)(implicit d1:DI,d2:DI,d3:DI,d4:DI,d5:DI,d6:DI,d7:DI,d8:DI):Long = {
	  getColumn(col) match {
	      case null => 0
	      case x:Number => x.asInstanceOf[Number].longValue()
	      case y:String => y.toLong
	  }
	}

	def apply(col:String)(implicit d1:DI,d2:DI,d3:DI,d4:DI,d5:DI,d6:DI,d7:DI,d8:DI,d9:DI,d10:DI,d11:DI):Option[Long] = {
	  getColumn(col) match {
	      case null => None
	      case x:Number => Some(x.asInstanceOf[Number].longValue())
	      case y:String => Some(y.toLong)
	  }
	}

	def apply(col:String)(implicit d1:DI,d2:DI,d3:DI):String = {
	  getColumn(col) match {
	      case null => null
	      case x:String => x
	      case z:Array[Byte] => new String(z, "UTF-8")
	      case y => y.toString()
	  }
	}
  
	def apply(col:String)(implicit d1:DummyImplicit,d2:DI,d3:DI,d4:DI):Option[String] = {
	  getColumn(col) match {
	      case null => None
	      case x:String => Some(x)
	      case y => Some(y.toString())
	  }
	}

	def apply(col:String)(implicit d1:DI,d2:DI,d3:DI,d4:DI,d5:DI):java.sql.Date = {
	  getColumn(col) match {
	      case null => null
	      case x:java.sql.Date => x
	      case y => assert(false); null
	  }
	}
  
	def apply(col:String)(implicit d1:DI,d2:DI,d3:DI,d4:DI,d5:DI,d6:DI):Option[java.sql.Date] = {
	  getColumn(col) match {
	      case null => None
	      case x:java.sql.Date => Some(x)
	      case y => assert(false); None
	  }
	}

	def apply(col:String)(implicit d1:DI,d2:DI,d3:DI,d4:DI,d5:DI,d6:DI,d7:DI,d8:DI,d9:DI):Timestamp = {
	  getColumn(col) match {
	      case null => null
	      case x:Timestamp => x
	      case y => assert(false); null
	  }
	}
  
	def apply(col:String)(implicit d1:DI,d2:DI,d3:DI,d4:DI,d5:DI,d6:DI,d7:DI,d8:DI,d9:DI,d10:DI):Option[Timestamp] = {
	  getColumn(col) match {
	      case null => None
	      case x:Timestamp => Some(x)
	      case y => assert(false); None
	  }
	}
  
	def apply(col:String)(implicit d1:DI,d2:DI,d3:DI,d4:DI,d5:DI,d6:DI,d7:DI):Boolean = {
	  getColumn(col) match {
	      case null => false
	      case x:java.lang.Boolean => x
	      case y:Number => y.longValue() != 0
	  }
	}

	def apply(col:String)(implicit d1:DI,d2:DI,d3:DI,d4:DI,d5:DI,d6:DI,d7:DI,d8:DI,d9:DI,d10:DI,d11:DI,d12:DI)
  	:Option[java.math.BigDecimal] = {
      val value = row.get(col)
	  value match {
	      case null => None
	      case y:java.math.BigDecimal => Some(y)
	      case x:String => Some(new java.math.BigDecimal(x))
	      case z:java.lang.Long => Some(java.math.BigDecimal.valueOf(z))
	      case w:java.lang.Double => Some(java.math.BigDecimal.valueOf(w))
	      case _ => assert(false); None
	  }
	}

	def apply(col:String)(implicit d1:DI,d2:DI,d3:DI,d4:DI,d5:DI,d6:DI,d7:DI,d8:DI,d9:DI,d10:DI,d11:DI,d12:DI,d13:DI)
  	:java.math.BigDecimal = {
      val value = row.get(col)
	  value match {
	      case null => null
	      case y:java.math.BigDecimal => y
	      case x:String => new java.math.BigDecimal(x)
	      case z:java.lang.Long => java.math.BigDecimal.valueOf(z)
	      case w:java.lang.Double => java.math.BigDecimal.valueOf(w)
	      case _ => assert(false); null
	  }
	}
}

protected object Row {
	def apply(row:java.util.Map[String,AnyRef]) = new Row(row)
}

trait DataSourceSupport {
	private var dataSource:DataSource = _
	private var jdbcTemplate:org.springframework.jdbc.core.JdbcTemplate = _
	private var namedParameterJdbcTemplate:org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate = _
	
	@Autowired def setDataSource(dataSource:DataSource):Unit = {
		this.dataSource = dataSource
		this.jdbcTemplate = new org.springframework.jdbc.core.JdbcTemplate(dataSource)
		this.namedParameterJdbcTemplate = new org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate(dataSource)
	}

	private def toJavaObjectSeq(args:Any*):Seq[Object] = args.map { x=>
	    if (x == None || x == null) {
	      null
	    } else if (x.isInstanceOf[Some[Any]]){
	    	x.asInstanceOf[Some[Any]].get.asInstanceOf[Object]
	    } else {
	    	x.asInstanceOf[Object]
	    }
	}

	private def toJavaObjectMap(paramMap:Map[String,Any]):Map[String,Object] = paramMap.map { x=>
	  (x._1, 
	    if (x._2 == None || x._2 == null) {
	      null
	    } else if (x._2.isInstanceOf[Some[Any]]){
	    	x._2.asInstanceOf[Some[Any]].get.asInstanceOf[Object]
	    } else {
	    	x._2.asInstanceOf[Object]
	    }
	  )
	}
	
	protected def execute(sql:String) = {
		jdbcTemplate.execute(sql)
	}

	protected def queryForSingleRow(sql:String, args:Any*):Option[Row] = 
		jdbcTemplate.queryForList(sql, toJavaObjectSeq(args:_*):_*).headOption.map(Row(_))
  
	protected def queryForSeq(sql:String, paramMap:Map[String,Any]):Seq[Row] =
		namedParameterJdbcTemplate.queryForList(sql, paramMap).map(Row(_))

  	protected def queryForSeq(sql:String, args:Array[AnyRef], argTypes:Array[Int]) = 
  	  	jdbcTemplate.queryForList(sql, args, argTypes).map(Row(_))

  	protected def queryForSeq(sql:String, args:Any*):Seq[Row] =
  		jdbcTemplate.queryForList(sql, toJavaObjectSeq(args:_*):_*).map(Row(_))

  	protected def queryForString(sql:String, args:Any*):String = 
  		jdbcTemplate.queryForList(sql, classOf[String], toJavaObjectSeq(args:_*):_*).head

  	protected def queryForString(sql:String, args:Any*)(implicit di1:DummyImplicit):Option[String] = 
  		jdbcTemplate.queryForList(sql, classOf[String], toJavaObjectSeq(args:_*):_*).headOption
	
  	protected def queryForInt(sql:String, args:Any*):Int = 
  		jdbcTemplate.queryForList(sql, classOf[java.lang.Long], toJavaObjectSeq(args:_*):_*).headOption.map(_.intValue).getOrElse(0)

  	protected def queryForInt(sql:String, args:Any*)(implicit di1:DummyImplicit):Option[Int] = 
  		jdbcTemplate.queryForList(sql, classOf[java.lang.Long], toJavaObjectSeq(args:_*):_*).headOption.map(_.intValue)

  	protected def queryForLong(sql:String, args:Any*):Long =
  		jdbcTemplate.queryForList(sql, classOf[java.lang.Long], toJavaObjectSeq(args:_*):_*).headOption.map(_.longValue).getOrElse(0)

  	protected def queryForLong(sql:String, args:Any*)(implicit di1:DummyImplicit):Option[Long] =
  		jdbcTemplate.queryForList(sql, classOf[java.lang.Long], toJavaObjectSeq(args:_*):_*).headOption.map(_.longValue)

  	protected def update(sql:String, paramMap:Map[String,Any]):Int = namedParameterJdbcTemplate.update(sql, paramMap)

  	protected def update(sql:String, args:Any*):Int = jdbcTemplate.update(sql, toJavaObjectSeq(args:_*):_*)
}
