"""Kiểm tra chế độ giải cứu con tin: python3 tools/rescuetest.py"""
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
        pg.on('console', lambda m: errs.append('console: '+m.text) if m.type=='error' and '404' not in m.text else None)
        await pg.goto('http://127.0.0.1:8799/'); await pg.wait_for_function('window.__gameReady===true')
        ev=pg.evaluate
        async def gwait(sec):
            t0=await ev("window.__game.state.time"); await pg.wait_for_function(f"window.__game.state.time>{t0}+{sec}")
        for mp in ('cuchi','a1','khesanh'):
            await ev(f"(async()=>{{ const g=window.__game; g.settings.map='{mp}'; g.settings.mode='rescue'; await g.startCampaign(); }})()")
            await pg.wait_for_function("window.__game.state.phase==='playing'")
            R[mp]=await ev("(()=>{ const g=window.__game; return {mission:g.state.mission, hostages:g.hostages.length, captive:g.hostages.filter(h=>h.state==='captive').length, enemies:g.enemies.length, allies:g.allies.length, obj:document.getElementById('obj').textContent}; })()")
            # tới con tin và giữ E
            await ev("(()=>{ const g=window.__game, h=g.hostages[0]; g.player.invuln=999; g.player.pos.set(h.pos.x+1,0,h.pos.z); for(const e of g.enemies){ e.react=999; e.cool=999; } })()")
            await pg.keyboard.down('e'); await gwait(2.2); await pg.keyboard.up('e')
            R[mp+'_after']=await ev("(()=>{ const g=window.__game; return {freed:g.state.freed, h0:g.hostages[0].state, obj:document.getElementById('obj').textContent}; })()")
            await gwait(2); await pg.screenshot(path=f'{shots}/rescue_{mp}.png')
        await b.close()
    return errs, R
check.prep(); pr=check.server()
try:
    errs,R=asyncio.run(run()); print(json.dumps({'errors':errs[:15],'report':R},ensure_ascii=False,indent=1))
finally: pr.terminate()
