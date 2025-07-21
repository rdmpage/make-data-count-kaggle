<?xml version='1.0' encoding='utf-8'?>
<xsl:stylesheet version='1.0' 
xmlns:xsl='http://www.w3.org/1999/XSL/Transform' xmlns:xlink='http://www.w3.org/1999/xlink' xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:tp="http://www.plazi.org/taxpub"
>

<xsl:output method='xml' version='1.0' encoding='utf-8' indent='yes'/>

<!-- ensure that elements that we don't explicitly match are spaced (e.g., in references) -->
<xsl:preserve-space elements="*"/>

<!--

we sometimes have (e.g. 10.1242_dev.138545 where headings aren't semantic)

      <fn>
        <p>
          <bold>Data availability</bold>
        </p>
        <p>Microarray expression data are available from the Dryad Digital Repository at 
        <uri xlink:href="http://dx.doi.org/10.5061/dryad.fj0qj">http://dx.doi.org/10.5061/dryad.fj0qj</uri>(
        <xref rid="DEV138545C67" ref-type="bibr">Miyazawa et al., 2016</xref>).</p>
      </fn>

-->

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

	<!-- eat for now -->
    <xsl:template match="front">
    	 <xsl:apply-templates select="notes"/>
    </xsl:template>

    <xsl:template match="body">
        <xsl:apply-templates/>
    </xsl:template>
    
    <xsl:template match="back">
    	<xsl:apply-templates/>
    	<!--
        <xsl:apply-templates select="ack"/>
        <xsl:apply-templates select="notes"/>
        <xsl:apply-templates select="fn-group"/>
        <xsl:apply-templates select="ref-list"/>   
        -->     
    </xsl:template>
    
    <xsl:template match="sec">
    	<section id="{generate-id()}">
    		<!--
        	<xsl:attribute name="id">
        		<xsl:value-of select="@id" />
        	</xsl:attribute>
        	-->
        	
        	<xsl:choose>
        		<!-- do we have asec-type attribute? -->
        		<xsl:when test="@sec-type">
					
					<xsl:choose>   		

						 <xsl:when test="@sec-type='intro'">
							<type><xsl:text>Introduction</xsl:text></type>  
						 </xsl:when>

						 <xsl:when test="@sec-type='materials|methods'">
							<type><xsl:text>Methods</xsl:text></type>  
						 </xsl:when>

						 <xsl:when test="@sec-type='methods'">
							<type><xsl:text>Methods</xsl:text></type>  
						 </xsl:when>

						 <xsl:when test="@sec-type='discussion'">
							<type><xsl:text>Discussion</xsl:text></type>  
						 </xsl:when>
	
						 <xsl:when test="@sec-type='discussion|interpretation'">
							<type><xsl:text>Discussion</xsl:text></type>  
						 </xsl:when>

						 <xsl:when test="@sec-type='results'">
							<type><xsl:text>Results</xsl:text></type>  
						 </xsl:when>
						 
						 <xsl:when test="@sec-type='conclusions'">
							<type><xsl:text>Conclusions</xsl:text></type>  
						 </xsl:when>						 
						
						 <xsl:when test="@sec-type='supplementary-material'">
							<type><xsl:text>SupplementaryInformationDescription</xsl:text></type>  
						 </xsl:when>
						 
						 <xsl:when test="@sec-type='datasets'">
							<type><xsl:text>DatasetDescription</xsl:text></type>  
						 </xsl:when>						 

						 <xsl:when test="@sec-type='data-availability'">
							<type><xsl:text>DatasetDescription</xsl:text></type>  
						 </xsl:when>						 
						 
						 <xsl:otherwise>
						 	<type><xsl:value-of select="@sec-type" /></type>
						 </xsl:otherwise>
					</xsl:choose> 
					 		        		
        		</xsl:when>
        		<xsl:otherwise>
					<!-- try to type based on title -->
					<xsl:if test="title">
						<xsl:choose>   			
							 <xsl:when test="title='Acknowledgements'">
								<type><xsl:text>Acknowledgements</xsl:text></type> 
							 </xsl:when>

							 <xsl:when test="title='Availability of data and materials'">
								<type><xsl:text>DatasetDescription</xsl:text></type> 
							 </xsl:when>

							 <xsl:when test="title='OPEN RESEARCH BADGES'">
								<type><xsl:text>DatasetDescription</xsl:text></type> 
							 </xsl:when>

							 <xsl:when test="title='Background'">
								<type><xsl:text>Background</xsl:text></type> 
							 </xsl:when>

							 <xsl:when test="title='Competing interests'">
								<type><xsl:text>ConflictOfInterest</xsl:text></type> 
							 </xsl:when>		 
	
							 <xsl:when test="title='Conclusion'">
								<type><xsl:text>Conclusion</xsl:text></type> 
							 </xsl:when>
 	
 							 <xsl:when test="title='Conclusions'">
								<type><xsl:text>Conclusion</xsl:text></type> 
							 </xsl:when>
							 
							 <xsl:when test="title='Databases'">
								<type><xsl:text>DatasetDescription</xsl:text></type> 
							 </xsl:when>

							 <xsl:when test="title='Data availability'">
								<type><xsl:text>DatasetDescription</xsl:text></type> 
							 </xsl:when>

							 <xsl:when test="title='Data Availability'">
								<type><xsl:text>DatasetDescription</xsl:text></type> 
							 </xsl:when>

							 <xsl:when test="title='DATA AVAILABILITY STATEMENT'">
								<type><xsl:text>DatasetDescription</xsl:text></type> 
							 </xsl:when>
							 		
							 <xsl:when test="title='Discussion'">
								<type><xsl:text>Discussion</xsl:text></type> 
							 </xsl:when>
							 
							 <xsl:when test="title='Materials and Methods'">
								<type><xsl:text>Methods</xsl:text></type> 
							 </xsl:when>
		
							 <xsl:when test="title='Methods'">
								<type><xsl:text>Methods</xsl:text></type> 
							 </xsl:when>
		
							 <xsl:when test="title='Results'">
								<type><xsl:text>Results</xsl:text></type> 
							 </xsl:when>
						 
							 <xsl:otherwise>
							 	<!-- <type><xsl:value-of select="title" /></type> -->
							 </xsl:otherwise>
							 
						</xsl:choose>
					
					</xsl:if>
				
				</xsl:otherwise>
			</xsl:choose>
    		
        	<xsl:apply-templates/>
        </section>
    </xsl:template>
    
    <xsl:template match="p">
    	<p id="{generate-id()}">
        	<xsl:apply-templates/>
        </p>
    </xsl:template>
    
	<!-- table -->	
	<xsl:template match="table-wrap">
		<section id="{generate-id()}">	
			<type>Table</type>
				<xsl:apply-templates />
		</section>
	</xsl:template>	
	
	<!-- table -->
    <xsl:template match="table"><table  id="{generate-id()}" cellspacing="0" cellpadding="2"><xsl:apply-templates /></table></xsl:template>
    <xsl:template match="tr"><tr><xsl:apply-templates /></tr></xsl:template>
    <xsl:template match="th"><th><xsl:apply-templates /></th></xsl:template>
    <xsl:template match="td"><td id="{generate-id()}"><xsl:apply-templates /></td></xsl:template> 
    
    <!-- figure -->
    <xsl:template match="fig">
    	<figure>
			<figcaption>	 
				<type>Caption</type>	
    			<xsl:apply-templates />
    		</figcaption>	
    	</figure>
    </xsl:template>
    
	<!-- references -->
    <xsl:template match="ref-list">
    	<section id="{generate-id()}">
    		<type>References</type>
        	<!-- Kew JATS is broken and has ref-list twice(!) -->
        	<xsl:apply-templates />
        </section>
    </xsl:template>

    <!-- Reference list -->
    <xsl:template match="ref">
        <cite>  
        	<xsl:attribute name="id">
        		<xsl:value-of select="@id" />
        	</xsl:attribute>
        	
            <xsl:apply-templates select="mixed-citation"/>
            
            <!-- Hindawi -->
            <xsl:apply-templates select="nlm-citation"/>            
            
            <!-- Biodiversity Data Journal -->
            <xsl:apply-templates select="element-citation"/>
            
            <!-- Frontiers  -->
            <xsl:apply-templates select="citation"/>
            
        </cite>
    </xsl:template>
    
    <!-- a citation -->
    <xsl:template match="mixed-citation | element-citation | nlm-citation | citation">
		<xsl:apply-templates/>
		
		<!-- links -->
		<!--
		<xsl:for-each select="uri">
			<xsl:choose>
				<xsl:when test="@xlink:type='simple'">
					<xsl:text>  </xsl:text>
					<xsl:value-of select="." />
				</xsl:when>
				<xsl:otherwise>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:for-each>
		-->

		<!-- identifiers -->
		<!-- need to think about this -->
		
		<xsl:for-each select="ext-link">
			<xsl:choose>				
				<xsl:when test="@ext-link-type='uri'">
					<!--
				        <xsl:text>  </xsl:text>
						<xsl:value-of select="." />
					-->
				</xsl:when>
				<xsl:when test="@ext-link-type='doi'">
						<xsl:text>  </xsl:text>
						<xsl:value-of select="." />
				</xsl:when>
				
				<xsl:otherwise>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:for-each>
		
<!--
		<xsl:for-each select="pub-id">
			<xsl:choose>
				<xsl:when test="@pub-id-type='pmid'">
						<xsl:text> </xsl:text>
						<xsl:value-of select="." />
				</xsl:when>
				<xsl:when test="@pub-id-type='doi'">
						<xsl:text> </xsl:text>
						<xsl:value-of select="." />
				</xsl:when>
				
				<xsl:otherwise>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:for-each>
-->
				
</xsl:template>    

    <xsl:template match="person-group">  
    	
    	<xsl:value-of select="." />
    	
    	<xsl:apply-templates /> 
    	<xsl:text>|  </xsl:text>
    </xsl:template> 

	<!-- hack to ensure spacing between elements -->
    <xsl:template match="article-title | source | year | volume | spage | lpage">  
    	<xsl:value-of select="." />
    	<xsl:text>  </xsl:text>
    </xsl:template> 
 
     <xsl:template match="uri">  
    	<xsl:value-of select="." />
    	<xsl:text>  </xsl:text>
    </xsl:template> 
   
  
	
<!--
          <article-title>Low contribution of BRCA1/2 genomic rearrangement to high-risk breast cancer in the Korean population</article-title>
          <source>Familial Cancer</source>
          <year>2009</year>
          <volume>8</volume>
          <fpage>505</fpage>
          <lpage>508</lpage>
-->

    
    <!-- eat -->
    <xsl:template match="inline-formula">    
    </xsl:template> 

    <xsl:template match="title">    
    </xsl:template> 

     
    <!-- extra -->
    <xsl:template match="ack">
    	<section id="{generate-id()}">
        	<type>Acknowledgments</type>    		
        	<xsl:apply-templates/>
        </section>
    </xsl:template>
    
    
    <xsl:template match="notes"> 
    	<section id="{generate-id()}">
    		<b>Notes</b> 
    		
        	<xsl:choose>
        		<!-- do we have a content-type attribute? -->
        		<xsl:when test="@notes-type">
					
					<xsl:choose>   		

						 <xsl:when test="@notes-type='author-contributions'">
							<type><xsl:text>AuthorContribution</xsl:text></type>  
						 </xsl:when>

						 <xsl:when test="@notes-type='COI-statement'">
							<type><xsl:text>ConflictOfInterest</xsl:text></type>  
						 </xsl:when>

						 <xsl:when test="@notes-type='funding-information'">
							<type><xsl:text>Acknowledgements</xsl:text></type>  
						 </xsl:when>
						 
						 <xsl:when test="@notes-type='data-availability'">
							<type><xsl:text>DatasetDescription</xsl:text></type> 						
						 </xsl:when>
						 
						<xsl:otherwise>
						</xsl:otherwise>
						 
					</xsl:choose>  
				</xsl:when>
				<xsl:otherwise>
					<!-- try to type based on title -->
					<xsl:if test="title">
						<xsl:choose>   			

							 <xsl:when test="title='Data Availability'">
								<type><xsl:text>DatasetDescription</xsl:text></type> 
							 </xsl:when>

							 <xsl:when test="title='Data availability'">
								<type><xsl:text>DatasetDescription</xsl:text></type> 
							 </xsl:when>
						 
							 <xsl:otherwise>
							 	<!-- <type><xsl:value-of select="title" /></type> -->
							 </xsl:otherwise>
							 
						</xsl:choose>
					
					</xsl:if>
				</xsl:otherwise>
			</xsl:choose>
    		
    		 
    		<xsl:apply-templates />  
    	</section>
    </xsl:template> 

    <xsl:template match="fn-group"> 
    	<section id="{generate-id()}">

        	<xsl:choose>
        		<!-- do we have a content-type attribute? -->
        		<xsl:when test="@content-type">
					
					<xsl:choose>   		

						 <xsl:when test="@content-type='author-contributions'">
							<type><xsl:text>AuthorContribution</xsl:text></type>  
						 </xsl:when>

						 <xsl:when test="@content-type='competing-interests'">
							<type><xsl:text>ConflictOfInterest</xsl:text></type>  
						 </xsl:when>
						 
						 <xsl:when test="@content-type='other'">
							<type><xsl:text>DatasetDescription</xsl:text></type> 						
						 </xsl:when>
						 
						<xsl:otherwise>
						</xsl:otherwise>
						 
					</xsl:choose>  
				</xsl:when>
				<xsl:otherwise>
				</xsl:otherwise>
			</xsl:choose>
    	
    	
     		<xsl:apply-templates />  
    	</section>
    </xsl:template> 
    
    <xsl:template match="supplementary-material"> 
    	<section id="{generate-id()}">
    		<type><xsl:text>SupplementaryInformationDescription</xsl:text></type>  
    		<xsl:apply-templates />  
    	</section>
    </xsl:template> 
    
    


</xsl:stylesheet>
