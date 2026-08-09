import fs from 'node:fs';
import https from 'node:https';

const rawData = fs.readFileSync('stitch_data.json', 'utf8');
const data = JSON.parse(rawData);

console.log("=== PROJECT DETAILS ===");
console.log(JSON.stringify(data.projectRes, null, 2));

console.log("\n=== SCREEN DETAILS SUMMARY ===");
data.screenDetails.forEach((item, index) => {
  console.log(`\n--- Screen #${index + 1} ---`);
  console.log("Title:", item.screen.title);
  console.log("Name:", item.screen.name);
  console.log("Detail keys:", Object.keys(item.detail));
  console.log("Detail result content:", JSON.stringify(item.detail.result, null, 2).substring(0, 500));
});
