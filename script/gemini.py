import urllib.request
import os
import json

ver = os.getenv('GEMINI_CLI_VERSION')
dep_ver = os.getenv('NODE_PTY_VERSION')

assert ver is not None, "GEMINI_CLI_VERSION environment variable must be set"
assert dep_ver is not None, "NODE_PTY_VERSION environment variable must be set"

if os.path.exists('gemini-cli'):
    os.rmdir('gemini-cli')

os.mkdir('gemini-cli')
urllib.request.urlretrieve(f"https://github.com/google-gemini/gemini-cli/releases/download/v{ver}/gemini.js", "gemini-cli/gemini.js")

with open('gemini-cli/package.json', 'w') as f:
    cfg = dict()
    cfg['name'] = 'gemini-cli'
    cfg['version'] = ver 
    cfg['bin'] = dict()
    cfg['bin']['gemini'] = 'gemini.js'
    cfg['dependencies'] = dict()
    cfg['dependencies']['node-pty'] = f'github:microsoft/node-pty#v{dep_ver}'
    f.write(json.dumps(cfg))

os.system("bun install --cwd gemini-cli --production")
os.system("tar -czf gemini-cli.tar.gz gemini-cli")
