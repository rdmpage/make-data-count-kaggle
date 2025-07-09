<?xml version='1.0' encoding='utf-8'?>
<xsl:stylesheet version='1.0' 
xmlns:xsl='http://www.w3.org/1999/XSL/Transform' 
xmlns:xlink='http://www.w3.org/1999/xlink' 
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
		<xsl:apply-templates/>
	</article>
	
	</body>
	</html>
</xsl:template>

    <xsl:template match="passage">
    	<!-- https://stackoverflow.com/a/1710229 -->
    	<section id="{generate-id()}">
    		<xsl:apply-templates/>
    	</section>
    </xsl:template>
    
     
	 <xsl:template match="infon">
		<xsl:choose>
		
			<!-- map to my types -->
			<xsl:when test="@key='section_type'">
					<h2><xsl:value-of select="." /></h2>
					
					<type>
					<xsl:choose>
					
    			    	<xsl:when test=".='ABSTRACT'">
    			     		<xsl:text>Abstract</xsl:text>
    			     	</xsl:when>
    			     	
     			    	<xsl:when test=".='COMP_INT'">
    			     		<xsl:text>ConflictOfInterest</xsl:text>
    			     	</xsl:when>

   			    		<xsl:when test=".='DISCUSS'">
    			     		<xsl:text>Discussion</xsl:text>
    			     	</xsl:when>

     			    	<xsl:when test=".='FIG'">
    			     		<xsl:text>Figure</xsl:text>
    			     	</xsl:when>

	   			    	<xsl:when test=".='INTRO'">
    			     		<xsl:text>Introduction</xsl:text>
    			     	</xsl:when>

    			    	<xsl:when test=".='METHODS'">
    			     		<xsl:text>Methods</xsl:text>
    			     	</xsl:when>

    			    	<xsl:when test=".='RESULTS'">
    			     		<xsl:text>Results</xsl:text>
    			     	</xsl:when>

    			    	<xsl:when test=".='REF'">
    			     		<xsl:text>References</xsl:text>
    			     	</xsl:when>

    			    	<xsl:when test=".='SUPPL'">
    			     		<xsl:text>SupplementaryInformationDescription</xsl:text>
    			     	</xsl:when>

    			    	<xsl:when test=".='TABLE'">
    			     		<xsl:text>Table</xsl:text>
    			     	</xsl:when>
    			     	
    			      	<xsl:otherwise>
    			     	</xsl:otherwise>
    				</xsl:choose>
    				</type>

					
			</xsl:when>
			
			<xsl:when test="@key='type'">
				<xsl:choose>
				
					<xsl:when test=". = 'ref'">
						<cite id="{generate-id()}">
							<xsl:value-of select="../text"/>
						</cite>								
					</xsl:when>

					<xsl:when test=". = 'paragraph'">
						<p id="{generate-id()}">
							<xsl:value-of select="../text"/>
						</p>								
					</xsl:when>
					
					<xsl:when test=". = 'fig_caption'">
						<figure>
							<figcaption>
								<xsl:value-of select="../text"/>
							</figcaption>	
						</figure>							
					</xsl:when>
					
					<xsl:when test=". = 'table'">
						<p id="{generate-id()}">
							<xsl:value-of select="../text"/>
						</p>								
					</xsl:when>
					
				<xsl:otherwise>
						<p id="{generate-id()}">
							<xsl:apply-templates/>
						</p>								
				</xsl:otherwise>
				</xsl:choose>
			</xsl:when>
			
			<xsl:otherwise>
			</xsl:otherwise>
		</xsl:choose>
	 </xsl:template>
    

    <xsl:template match="text">
    	<!-- <xsl:value-of select="." /> -->
    </xsl:template>

    
    <!-- eat -->
    <xsl:template match="offset">
    </xsl:template>
    <xsl:template match="source">
    </xsl:template>
    <xsl:template match="date">
    </xsl:template>
    <xsl:template match="key">
    </xsl:template>
    <xsl:template match="id">
    </xsl:template>

</xsl:stylesheet> 

