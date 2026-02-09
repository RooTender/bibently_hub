const fs = require('fs');

const path = 'package.json';
const pkg = JSON.parse(fs.readFileSync(path, 'utf8'));

if (pkg.scripts && pkg.scripts.prepare) {
  console.log('Removing prepare script...');
  delete pkg.scripts.prepare;
  fs.writeFileSync(path, JSON.stringify(pkg, null, 2));
} else {
  console.log('No prepare script found.');
}
