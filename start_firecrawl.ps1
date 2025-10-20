$env:FIRECRAWL_API_KEY = "fc-c85aefe745134a5f8ed1e376e3d57457"
$env:HTTP_STREAMABLE_SERVER = "true"
Set-Location "D:\Recruitment"
$npx = "npx -y firecrawl-mcp"
& cmd /c $npx *> firecrawl_server.log
