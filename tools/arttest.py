"""Kiểm tra hiệu ứng bắn pháo + camera bám đạn: python3 tools/arttest.py"""
import asyncio, os, sys, json
sys.argv=[sys.argv[0]]+(sys.argv[1:] or ['high'])
import check
async def run():
    from playwright.async_api import async_playwright
    shots=f'{check.ROOT}/tools/shots'; errs=[]; R={}
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome' if os.path.exists('/usr/bin/google-chrome') else None, args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
        ctx=await b.new_context(viewport={'width':960,'height':540}); await ctx.add_init_script(f"try{{localStorage.setItem('tl_quality3', JSON.stringify('{check.Q}'))}}catch(e){{}}")
        pg=await ctx.new_page(); pg.set_default_timeout(400000)
        pg.on('pageerror', lambda e: errs.append('pageerror: '+str(e)))
        await pg.goto('http://127.0.0.1:8799/'); await pg.wait_for_function('window.__gameReady===true')
        ev=pg.evaluate
        async def gwait(sec):
            t0=await ev("window.__game.state.time"); await pg.wait_for_function(f"window.__game.state.time>{t0}+{sec}")
        await ev("(async()=>{ const g=window.__game; g.settings.map='khesanh'; g.settings.mode='base'; await g.startCampaign(); })()")
        await pg.wait_for_function("window.__game.state.phase==='playing'")
        await ev("(()=>{ const g=window.__game; const a=g.arts.slice().sort((p,q)=>p.x-q.x)[0]; a.gunner=null; g.player.invuln=999; g.player.pos.set(a.x+2,0,a.z); g.mountArt(a); g.player.yaw=-Math.PI/2; g.player.pitch=0.35; a.cool=0; g.player.fireHeld=true; })()")
        await gwait(0.12); await ev("window.__game.player.fireHeld=false")
        await pg.screenshot(path=f'{shots}/art_1_fire.png')
        await gwait(0.5); await pg.screenshot(path=f'{shots}/art_2_flight.png')
        R['cam']=await ev("window.__game.shellCam.on")
        await gwait(1.4); await pg.screenshot(path=f'{shots}/art_3_flight.png')
        for k in range(20):
            if not await ev("window.__game.shells.length>0"): break
            await gwait(0.3)
        await pg.screenshot(path=f'{shots}/art_4_impact.png'); await gwait(0.2); await pg.screenshot(path=f'{shots}/art_5_impact.png')
        await gwait(2.5); R['camAfter']=await ev("window.__game.shellCam.on"); R['onArt']=await ev("!!window.__game.player.onArt")
        await b.close()
    return errs, R
check.prep(); pr=check.server()
try:
    errs,R=asyncio.run(run()); print(json.dumps({'errors':errs,'report':R},ensure_ascii=False)); print('KẾT QUẢ:', 'ĐẠT' if not errs else 'CÓ LỖI')
finally: pr.terminate()
