import fs from 'node:fs';

let logStr = "";

logStr += "=== LOGIN SIGN UP SMART RAG HTML BODY ===\n";
if (fs.existsSync('login_sign_up_smart_rag.html')) {
  const html = fs.readFileSync('login_sign_up_smart_rag.html', 'utf8');
  const bodyMatch = html.match(/<body[^>]*>([\s\S]*)<\/body>/i);
  logStr += (bodyMatch ? bodyMatch[1] : html) + "\n";
}

logStr += "\n=== LOGIN SMART RAG LIGHT HTML BODY ===\n";
if (fs.existsSync('login_smart_rag_light_.html')) {
  const html = fs.readFileSync('login_smart_rag_light_.html', 'utf8');
  const bodyMatch = html.match(/<body[^>]*>([\s\S]*)<\/body>/i);
  logStr += (bodyMatch ? bodyMatch[1] : html) + "\n";
}

fs.writeFileSync('output_login.txt', logStr);
console.log("Wrote output_login.txt");
