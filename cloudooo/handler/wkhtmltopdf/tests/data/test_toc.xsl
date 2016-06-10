<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:outline="http://wkhtmltopdf.org/outline"
    xmlns="http://www.w3.org/1999/xhtml">
  <xsl:output method="html" encoding="utf-8" indent="yes" doctype-system="about:legacy-compat"/>

  <xsl:template match="outline:outline">
    <xsl:param name="count" select="0" />
    <html>
      <head>
        <title>Table of Contents</title>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <style>
          html, body {
            overflow-x: initial !important;
          }
        </style>
      </head>
      <body>
        <p class="ci-document-faux-h1">Table of Contents</p>
        <div class="ci-document-table-of-content">
          <p class="ci-document-helper"></p>
          <ol>
            <xsl:apply-templates select="outline:item/outline:item">
              <xsl:with-param name="count" select="$count" />
            </xsl:apply-templates>
          </ol>
        </div>
      </body>
    </html>
  </xsl:template>
  <xsl:template match="outline:item">
    <xsl:param name="count" />
      <xsl:choose>
        <xsl:when test="number($count)=0">
          <li class="ci-document-table-of-content-lead-item">
            <xsl:if test="@title!=''">
              <div>
                <a>
                  <xsl:if test="@link">
                    <xsl:attribute name="href"><xsl:value-of select="@link"/></xsl:attribute>
                  </xsl:if>
                  <xsl:if test="@backLink">
                    <xsl:attribute name="name"><xsl:value-of select="@backLink"/></xsl:attribute>
                  </xsl:if>
                  <xsl:value-of select="@title" />
                </a>
                <span><xsl:value-of select="@page" /> </span>
              </div>
            </xsl:if>
            <ol>
              <xsl:comment>added to prevent self-closing tags in QtXmlPatterns</xsl:comment>
              <xsl:apply-templates select="outline:item"></xsl:apply-templates>
            </ol>
          </li>
        </xsl:when>
        <xsl:otherwise>
          <li>
            <xsl:if test="@title!=''">
              <div>
                <a>
                  <xsl:if test="@link">
                    <xsl:attribute name="href"><xsl:value-of select="@link"/></xsl:attribute>
                  </xsl:if>
                  <xsl:if test="@backLink">
                    <xsl:attribute name="name"><xsl:value-of select="@backLink"/></xsl:attribute>
                  </xsl:if>
                  <xsl:value-of select="@title" />
                </a>
                <span><xsl:value-of select="@page" /> </span>
              </div>
            </xsl:if>
            <ol>
              <xsl:comment>added to prevent self-closing tags in QtXmlPatterns</xsl:comment>
              <xsl:apply-templates select="outline:item"></xsl:apply-templates>
            </ol>
          </li>
        </xsl:otherwise>
      </xsl:choose>
  </xsl:template>
</xsl:stylesheet>
