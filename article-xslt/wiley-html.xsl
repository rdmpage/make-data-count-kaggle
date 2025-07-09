<?xml version='1.0' encoding='utf-8'?>
<xsl:stylesheet version='1.0' 
xmlns:xsl='http://www.w3.org/1999/XSL/Transform' 
xmlns:xlink='http://www.w3.org/1999/xlink' 
xmlns:wiley="http://www.wiley.com/namespaces/wiley" 
xmlns:wiley2="http://www.wiley.com/namespaces/wiley/wiley"
exclude-result-prefixes="xlink wiley wiley2"
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
		<xsl:apply-templates match="//wiley:section"/>
	</article>
	
	</body>
	</html>
</xsl:template>

     
    <!-- section -->
    <xsl:template match="wiley:section">
    	<section id="{generate-id()}">
    	
    	<xsl:if test="@type">
    		<type>
    			<xsl:choose>
    			     <xsl:when test="@type='acknowledgments'">
    			     	<xsl:text>Acknowledgements</xsl:text>
    			     </xsl:when>
    			     
    			     <xsl:when test="@type='caption'">
    			     	<xsl:text>Caption</xsl:text>
    			     </xsl:when>
    			     
    			     <xsl:when test="@type='conclusions'">
    			     	<xsl:text>Conclusion</xsl:text>
    			     </xsl:when>
    			     
    			     <xsl:when test="@type='conflictOfInterest'">
    			     	<xsl:text>ConflictOfInterest</xsl:text>
    			     </xsl:when>
    			     
     			     <xsl:when test="@type='dataAvailability'">
    			     	<xsl:text>DatasetDescription</xsl:text>
    			     </xsl:when>   
    			      			     
   			     	 <xsl:when test="@type='discussion'">
    			     	<xsl:text>Discussion</xsl:text>
    			     </xsl:when>
    			     
    			     <xsl:when test="@type='materialsAndMethods'">
    			     	<xsl:text>Methods</xsl:text>
    			     </xsl:when>
    			     
    			     <xsl:when test="@type='methods'">
    			     	<xsl:text>Methods</xsl:text>
    			     </xsl:when>
    			     
    			     <xsl:when test="@type='opening'">
    			     	<xsl:text>Introduction</xsl:text>
    			     </xsl:when>   

    			     <xsl:when test="@type='openResearch'">
    			     	<xsl:text>DatasetDescription</xsl:text>
    			     </xsl:when>   
    			      			     
    			     <xsl:when test="@type='results'">
    			     	<xsl:text>Results</xsl:text>
    			     </xsl:when>
    			     
    			     <xsl:otherwise>
    			     	<xsl:value-of select="@type"/>
    			     </xsl:otherwise>
    			</xsl:choose>
    		</type>
    	</xsl:if>   	
    	
    	<!--
    	<h2>
    		<xsl:value-of select="wiley:title"/>
    	</h2>
    	-->
    	
    	<xsl:apply-templates/>
    	
    	</section>
    </xsl:template>
        
    <!-- paragraph -->
    <xsl:template match="wiley:p">
    	<p id="{generate-id()}">
    		<xsl:apply-templates/>
    	</p>
    </xsl:template>

    <!-- header -->
    <xsl:template match="wiley:header">
    
    	<!-- just for how it looks in the browser -->
     	<h1>
    		<xsl:value-of select="wiley:contentMeta/wiley:titleGroup/wiley:title"/>
    	</h1>
    
     	<title>
    		<xsl:value-of select="wiley:contentMeta/wiley:titleGroup/wiley:title"/>
    	</title>
    	
    	<xsl:if test="wiley:publicationMeta[@level='unit']/wiley:doi">
     		<doi>
      			<xsl:value-of select="wiley:publicationMeta[@level='unit']/wiley:doi"/>
     		</doi>
     	</xsl:if>

	</xsl:template>
    
   <xsl:template match="wiley:figure">
   		<figure id="{generate-id()}">
    		<xsl:apply-templates/>
    	</figure>
    </xsl:template>

   <xsl:template match="wiley:caption">
   		<figcaption>
    		<xsl:apply-templates/>
    	</figcaption>
    </xsl:template>
    
    
    <xsl:template match="wiley:bibliography">
    	<section id="{generate-id()}">
    	<type>References</type> <!-- I made this up -->
    	<title>
    		<xsl:value-of select="wiley:title"/>
    	</title>
    
    	<xsl:apply-templates/>
		</section>
    </xsl:template>
    
    <xsl:template match="wiley:bib">
    	<cite id="{generate-id()}">
    		<xsl:apply-templates/>
    	</cite>
    </xsl:template>
    
    <!-- 
    <xsl:template match="wiley:url">
			<a>
				<xsl:attribute name="href">
					<xsl:value-of select="." />
				</xsl:attribute>
				<xsl:value-of select="." />
			</a>
    </xsl:template>
    -->
    
    <xsl:template match="wiley:url">
    	<xsl:text> </xsl:text>
			<xsl:value-of select="." />
		<xsl:text> </xsl:text>
	</xsl:template>
       
    <xsl:template match="wiley:title">
    	<xsl:apply-templates/>
    </xsl:template>
    
    <xsl:template match="wiley:tabular">
     <section>
     	<type><xsl:text>Table</xsl:text></type>
     	
     	<table>
     		<xsl:if test="wiley:title">
     			<caption>
     				<xsl:value-of select="wiley:title" />	
     			</caption>
     		</xsl:if>
     		<xsl:apply-templates/>
     		
     	</table>
     </section>
    </xsl:template>
     

     <xsl:template match="wiley:table">
     	<xsl:apply-templates/>
    </xsl:template>


     <xsl:template match="wiley:tbody">
     <tbody>
     	<xsl:apply-templates/>
     </tbody>
    </xsl:template>

     <xsl:template match="wiley:thead">
     <thead>
     	<xsl:apply-templates/>
     </thead>
    </xsl:template>


    <xsl:template match="wiley:row">
    <tr>
    <xsl:apply-templates/>
    </tr>
    </xsl:template>

    <xsl:template match="wiley:entry">
    <td>
    <xsl:value-of select="." />
    </td>
    </xsl:template>

	<xsl:template match="text()">
		<xsl:value-of select="normalize-space(.)"/>
	</xsl:template>

</xsl:stylesheet> 
