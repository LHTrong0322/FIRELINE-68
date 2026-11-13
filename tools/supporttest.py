"""Kiểm tra mở đầu lịch sử, tiếp tế toàn đội, chi viện pháo binh / không kích: python3 tools/supporttest.py [high]"""
import asyncio, os, sys, json
sys.argv=[sys.argv[0]]+(sys.argv[1:] or ['high'])
import check
async def run():
    from playwright.async_api import async_playwright
    shots=f'{check.ROOT}/tools/shots'; errs=[]; rep={}
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome' if os.path.exists('/usr/bin/google-chrome') else None, args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
        ctx=await b.new_context(viewport={'width':960,'height':540}); await ctx.add_init_script(f"try{{localStorage.setItem('tl_quality4', JSON.stringify('{check.Q}'))}}catch(e){{}}")
        pg=await ctx.new_page(); pg.set_default_timeout(300000); pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://127.0.0.1:8799/'); await pg.wait_for_function('window.__gameReady===true', timeout=300000)
        await pg.evaluate("window.__forceIntro=true; (async()=>{ const g=window.__game; g.settings.map='khesanh'; g.settings.mode='base'; g.startCampaign(); })()")
        await pg.wait_for_function("!document.getElementById('intro').classList.contains('hidden')", timeout=200000)
        await pg.wait_for_timeout(9000); await pg.screenshot(path=f'{shots}/support_intro.png')
        await pg.evaluate("document.getElementById('intro').click(); document.getElementById('intro').click()")
        await pg.wait_for_function("window.__game.state.phase==='playing'", timeout=60000)
        await pg.evaluate("(()=>{ const g=window.__game; g.player.invuln=9999; g.teamSupply(); g.teamSupply(); })()"); await pg.wait_for_timeout(1500)
        await pg.screenshot(path=f'{shots}/support_panel.png')
        rep['support']=await pg.evaluate("window.__game.state.support.slice()")
        await pg.evaluate("window.__game.openSupMap()"); await pg.wait_for_timeout(800); await pg.screenshot(path=f'{shots}/support_map.png')
        await pg.evaluate("document.getElementById('artMapClose').click()")
        await pg.evaluate("(()=>{ const g=window.__game,p=g.player; const fx=-Math.sin(p.yaw), fz=-Math.cos(p.yaw); g.callSupport('air', p.pos.x+fx*40, p.pos.z+fz*40); p.pitch=0.15; g.state.timeScale=3; })()")
        t0=await pg.evaluate("window.__game.state.time"); await pg.wait_for_function(f"window.__game.state.time>{t0}+4.6", timeout=900000); await pg.screenshot(path=f'{shots}/support_air.png')
        await pg.evaluate("(()=>{ const g=window.__game,p=g.player; const fx=-Math.sin(p.yaw), fz=-Math.cos(p.yaw); g.callSupport('phao', p.pos.x+fx*35, p.pos.z+fz*35); })()")
        t0=await pg.evaluate("window.__game.state.time"); await pg.wait_for_function(f"window.__game.state.time>{t0}+5.2", timeout=900000); await pg.screenshot(path=f'{shots}/support_phao.png')
        rep['left']=await pg.evaluate("window.__game.state.support.length"); rep['strikes']=await pg.evaluate("window.__game.strikes.length")
        await b.close()
    return errs, rep
check.prep(); pr=check.server()
try: errs,rep=asyncio.run(run())
finally: pr.terminate()
print(json.dumps({'errors':errs,'report':rep},ensure_ascii=False)); print('KẾT QUẢ:', 'ĐẠT' if not errs and rep.get('left')==0 else 'CÓ LỖI')
