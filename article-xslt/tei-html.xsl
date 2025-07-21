<?xml version='1.0' encoding='utf-8'?>
<xsl:stylesheet version='1.0' 
xmlns:xsl='http://www.w3.org/1999/XSL/Transform' 
xmlns:xlink='http://www.w3.org/1999/xlink' 
xmlns:mml="http://www.w3.org/1998/Math/MathML" 
xmlns:tei="http://www.tei-c.org/ns/1.0"

>

<xsl:output method='xml' version='1.0' encoding='utf-8' indent='yes'/>

<xsl:template match="/">
	<html>
	<head>
	<style type="text/css">	
		body {
			line-height:1.5em;
			font-size:1em;
			padding:2em;
		}
		h1 {
			line-height:1em;
		}
		
		p {
			padding:1em;
			border:1px solid black;
			background-color:yellow;
		}

		section {
			border:1px solid red;
			padding:1em;
			background-color:rgba(255,0,0,0.3);
		}
		
		figure {
			background-color:orange;
			padding:1em;
		}
		
		cite {
			display:block;
			line-height:1.5em;
			padding:1em;
		}		
	</style>
	</head>
	<body>
	
	<article>
	<!-- for browser -->
	
	<!--
	<h1>
		<xsl:value-of select="//tei:teiheader/tei:filedesc/tei:titlestmt/tei:title" />
	</h1>
	-->
	
	
	<!--
	<title>
		<xsl:value-of select="//tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title" />
	</title> 
	-->
	
	<xsl:apply-templates select="//tei:text" />
	
	</article>
	</body>
	</html>
</xsl:template>

	<!--
    <xsl:template match="tei:teiHeader">
    </xsl:template>
    -->
    
    <xsl:template match="tei:text">
    	<xsl:apply-templates />
    </xsl:template>
    

    <!-- GROBID has structured references -->
    <!-- note that we may get camel Case and all lowercase tag names :( -->
    <xsl:template match="tei:biblstruct">
        <cite>
        	<xsl:if test="@xml:id">
				<xsl:attribute name="id">
					<xsl:value-of select="@xml:id" />
				</xsl:attribute>
      		</xsl:if>
        	
 			<xsl:apply-templates select="tei:note"/>  

 			<xsl:apply-templates select="*/tei:idno"/> 

 		</cite>
    </xsl:template>
    
    <xsl:template match="tei:biblStruct">
        <cite>
        	<xsl:if test="@xml:id">
				<xsl:attribute name="id">
					<xsl:value-of select="@xml:id" />
				</xsl:attribute>
       		</xsl:if>
       		
       		<!-- GROBID when I use it -->
       		<xsl:value-of select="." />
        	
 			<xsl:apply-templates select="tei:note"/>  
 			
 			<xsl:apply-templates select="*/tei:idno"/> 

 		</cite>
    </xsl:template>
    
    
    <!-- just show raw reference -->
   <xsl:template match="tei:note">
      <xsl:choose>
      	<xsl:when test="@type='raw_reference'">
      		<xsl:value-of select="." />
      	</xsl:when>
      	<xsl:otherwise>
      		<!-- eat -->
      	</xsl:otherwise>
      </xsl:choose>      
    </xsl:template>
     
    <!-- links -->
    <!--
    <xsl:template match="tei:ptr">
			<a>
				<xsl:attribute name="href">
					<xsl:value-of select="@target" />
				</xsl:attribute>
				<xsl:value-of select="@target" />
			</a>
    </xsl:template>
    -->
    
    <!-- DOI -->
	<!--
    <xsl:template match="tei:idno">
    	<xsl:if test="@type='DOI'">
    		<b><xsl:value-of select="." /></b>
    	</xsl:if>
    </xsl:template>
    -->
    
    <!-- section -->
    <xsl:template match="tei:div">
    	<section id="{generate-id()}">
    	
    		<xsl:choose>
				<xsl:when test="@type">
					<type>
					<xsl:choose>
					
						 <xsl:when test="@type='acknowledgement'">
							<xsl:text>Acknowledgements</xsl:text>
						 </xsl:when>
	 
						 <xsl:when test="@type='annex'">
							<xsl:text>DatasetDescription</xsl:text>
						 </xsl:when>
	
						 <xsl:when test="@type='availability'">
							<xsl:text>SupplementaryInformationDescription</xsl:text>
						 </xsl:when>
	
						 <xsl:when test="@type='funding'">
							<xsl:text>Acknowledgements</xsl:text>
						 </xsl:when>
	
						 <xsl:when test="@type='references'">
							<xsl:text>References</xsl:text>
						 </xsl:when>
						 
						 <xsl:otherwise>
							<xsl:value-of select="@type"/>
						 </xsl:otherwise>
					</xsl:choose>
					</type>
				</xsl:when>
				<xsl:otherwise>
					<xsl:choose>
					
						 <xsl:when test="text()[1]='Introduction'">
							<type><xsl:text>Introduction</xsl:text></type>
						 </xsl:when>
						 
						 <xsl:when test="text()[1]='Results'">
							<type><xsl:text>Results</xsl:text></type>
						 </xsl:when>						 

						 <xsl:when test="text()[1]='Conclusions'">
							<type><xsl:text>Conclusion</xsl:text></type>
						 </xsl:when>
						 
						 <xsl:when test="text()[1]='Appendix'">
							<type><xsl:text>SupplementaryInformationDescription</xsl:text></type>
						 </xsl:when>						 
						 
						 
						 <xsl:otherwise>
						 </xsl:otherwise>
					</xsl:choose>						
				</xsl:otherwise>
			</xsl:choose>	
       		
       		<!--
       		<h2>
       		<xsl:value-of select="text()[1]" />
       		</h2>
       		-->
       		
    	
    		<xsl:apply-templates/>
    	</section>
    </xsl:template>
    
    <!-- paragraph -->
    <xsl:template match="tei:p">
    	<p id="{generate-id()}">
    		<xsl:apply-templates/>
    	</p>
    </xsl:template>

	<!-- sentence -->
	<!--
    <xsl:template match="tei:s">
    	<xsl:apply-templates/>
    	<br />
    </xsl:template>
    -->
    
    <!-- figure -->
    <xsl:template match="tei:figure">
    	<section>
    		<xsl:choose>
    			<!-- table -->
    			<xsl:when test="@type='table'">
    				<xsl:apply-templates/>
    			</xsl:when>
    			
    			<xsl:otherwise>
    				<figure>
						<xsl:apply-templates/>
					</figure>
				</xsl:otherwise>
			</xsl:choose>
		</section>
    </xsl:template>

    <xsl:template match="tei:figdesc">
    	<caption>
    		<type>Caption</type>
    		<xsl:apply-templates/>
    	</caption>
    </xsl:template>

    <xsl:template match="tei:figDesc">
    	<caption>
    		<type>Caption</type>
    		<xsl:apply-templates/>
    	</caption>
    </xsl:template>
    
    
    <xsl:template match="tei:table">
    	<table>
    		<xsl:apply-templates/>
    	</table>
    </xsl:template>

    <xsl:template match="tei:row">
    	<tr>
    		<xsl:apply-templates/>
    	</tr>
    </xsl:template>

    <xsl:template match="tei:cell">
    	<td>
    		<xsl:value-of select="." />
    	</td>
    </xsl:template>
    
    <!-- eat -->

    <xsl:template match="tei:term">
    </xsl:template>

    <xsl:template match="tei:desc">
    </xsl:template>
    
    <xsl:template match="tei:listOrg">
     	<section id="{generate-id()}">
        	<xsl:if test="@type='funding'">
        		<type>Acknowledgements</type>
        	</xsl:if>
        	<xsl:apply-templates/>
 		</section>
 	 </xsl:template>
 
    <xsl:template match="tei:org">
    	<li>
    		<xsl:value-of select="." />
    	</li>
    </xsl:template>

    <xsl:template match="tei:idno">
    	<xsl:if test="@type='DOI'">
    		<doi>
    			<xsl:value-of select="." />
    		</doi>
    	</xsl:if>
    </xsl:template>
    
    

 
</xsl:stylesheet> 