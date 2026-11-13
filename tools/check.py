"""Kiểm tra tự động cho FIRELINE '68.
Chạy: python3 tools/check.py [low|med|high|ultra]
- Chạy game cục bộ qua `npx wrangler dev` (three.js lấy từ node_modules), mở bằng Chrome headless
- Báo lỗi JS, chụp ảnh vào tools/shots/, kiểm tra ảnh không bị đen/trắng toàn bộ
Thoát mã 0 nếu đạt, 1 nếu lỗi."""
import asyncio, os, re, shutil, subprocess, sys, time, json, urllib.request
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Q=sys.argv[1] if len(sys.argv)>1 else 'high'
TMP='/tmp/fireline_check'
def prep():
    shutil.rmtree(TMP, ignore_errors=True); shutil.copytree(ROOT, TMP, ignore=shutil.ignore_patterns('node_modules','.git','.wrangler','shots','__pycache__'))
    if not os.path.exists('/tmp/fl_three/node_modules/three'):
        os.makedirs('/tmp/fl_three', exist_ok=True); subprocess.run('npm init -y >/dev/null && npm i three@0.160.0 --no-audit --no-fund', shell=True, cwd='/tmp/fl_three', check=True)
    shutil.copytree('/tmp/fl_three/node_modules/three/build', f'{TMP}/public/three/build'); shutil.copytree('/tmp/fl_three/node_modules/three/examples', f'{TMP}/public/three/examples')
    p=f'{TMP}/public/index.html'; h=open(p).read()
    h=h.replace('https://cdn.jsdelivr.net/npm/three@0.160.0/','/three/'); h=re.sub(r'<link href="https://fonts.googleapis.com[^>]*>','',h); open(p,'w').write(h)
    if not os.path.exists(f'{ROOT}/node_modules/wrangler'): subprocess.run('npm i --no-audit --no-fund', shell=True, cwd=ROOT, check=True)
    os.symlink(f'{ROOT}/node_modules', f'{TMP}/node_modules')
def server():
    pr=subprocess.Popen('npx wrangler dev --port 8799 --ip 127.0.0.1', shell=True, cwd=TMP, stdout=open('/tmp/fl_wrangler.log','w'), stderr=subprocess.STDOUT)
    for _ in range(90):
        try: urllib.request.urlopen('http://127.0.0.1:8799/', timeout=2); return pr
        except Exception: time.sleep(1)
    raise SystemExit('wrangler dev không khởi động được')
async def run():
    from playwright.async_api import async_playwright
    shots=f'{ROOT}/tools/shots'; os.makedirs(shots, exist_ok=True)
    errs=[]
    async with async_playwright() as p:
        exe='/usr/bin/google-chrome' if os.path.exists('/usr/bin/google-chrome') else None
        b=await p.chromium.launch(executable_path=exe, args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
        ctx=await b.new_context(viewport={'width':960,'height':540}); await ctx.add_init_script(f"try{{localStorage.setItem('tl_quality4', JSON.stringify('{Q}'))}}catch(e){{}}")
        pg=await ctx.new_page(); pg.set_default_timeout(240000)
        pg.on('pageerror', lambda e: errs.append('pageerror: '+str(e)))
        pg.on('console', lambda m: errs.append('console: '+m.text) if m.type=='error' and '404' not in m.text else None)
        await pg.goto('http://127.0.0.1:8799/'); await pg.wait_for_function('window.__gameReady===true', timeout=300000)
        await pg.wait_for_timeout(1500); await pg.screenshot(path=f'{shots}/menu.png')
        await pg.evaluate("window.__game.startCampaign(); window.__game.state.waveT=999")
        await pg.wait_for_timeout(2500); await pg.screenshot(path=f'{shots}/play.png')
        await pg.evaluate("""(()=>{const g=window.__game; const p=g.player; p.pos.set(13.5*g.CELL,0,8.5*g.CELL); p.yaw=0; p.pitch=-0.03;
          ['rifle','mg','shotgun'].forEach(t=>g.spawnEnemy(t)); g.enemies.forEach((e,i)=>{ e.pos.set(13.5*g.CELL-1.4+i*1.4,0,8.5*g.CELL-3.2-i*0.6); e.react=99; e.cool=99; });})()""")
        await pg.wait_for_timeout(2500); await pg.screenshot(path=f'{shots}/enemies.png')
        await pg.evaluate("window.__game.player.fireHeld=true"); await pg.wait_for_timeout(400); await pg.screenshot(path=f'{shots}/fire.png')
        from PIL import Image, ImageStat
        lum=sum(ImageStat.Stat(Image.open(f'{shots}/{n}.png').convert('L')).mean[0] for n in ('play','enemies'))/2
        await b.close()
    return errs, lum
if __name__=='__main__':
    prep(); pr=server()
    try: errs,lum=asyncio.run(run())
    finally: pr.terminate()
    print(json.dumps({'quality':Q,'errors':errs[:20],'mean_luma':lum}, ensure_ascii=False, indent=1))
    ok = not errs and 8 < lum < 200
    print('KẾT QUẢ:', 'ĐẠT' if ok else 'KHÔNG ĐẠT'); sys.exit(0 if ok else 1)
