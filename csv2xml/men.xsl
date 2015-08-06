<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match="/">
  <html>
  <head>
    <style>
	h2 {
	   text-align: center;
	}
	table, td, th {
   	   border: 2px solid black;
	   padding: 3px 10px;

	}
	th {
	   background-color: #00aa00;
	   color: white;
	}
	table.men {
	   border-collapse: collapse;
	   margin-left: auto;
           margin-right: auto;

        }
    </style>
  </head>
  <body>
  <h2>The Men of Sherwood Forest</h2>
    <table class="men">
      <tr>
	<th>ID</th>
        <th>IP Address</th>
        <th>Port</th>
        <th>Active</th>	
      </tr>
      <xsl:for-each select="men/bot">
      <tr>
	<td><xsl:value-of select="@id" /></td>
        <td><xsl:value-of select="ipaddress"/></td>
        <td><xsl:value-of select="port"/></td>
        <td><xsl:value-of select="active"/></td> 
     </tr>
      </xsl:for-each>
    </table>
  </body>
  </html>
</xsl:template>
</xsl:stylesheet>

