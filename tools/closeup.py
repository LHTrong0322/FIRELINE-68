"""Chụp cận cảnh nhân vật để soi mô hình/hoạt ảnh: python3 tools/closeup.py [low|high]"""
import asyncio, os, sys
sys.argv=[sys.argv[0]]+(sys.argv[1:] or ['high'])
import check
async def run():
    from playwright.async_api import async_playwright
    shots=f'{check.ROOT}/tools/shots'; errs=[]
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome' if os.path.exists('/usr/bin/google-chrome') else None, args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
        ctx=await b.new_context(viewport={'width':960,'height':540}); await ctx.add_init_script(f"try{{localStorage.setItem('tl_quality4', JSON.stringify('{check.Q}'))}}catch(e){{}}")
        pg=await ctx.new_page(); pg.set_default_timeout(240000); pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://127.0.0.1:8799/'); await pg.wait_for_function('window.__gameReady===true', timeout=300000)
        await pg.evaluate("window.__game.settings.mode='rescue'; window.__game.startCampaign(); window.__game.state.waveT=999"); await pg.wait_for_timeout(2500)
        setup="""(()=>{const g=window.__game; const p=g.player; p.pos.set(13.5*g.CELL,0,8.5*g.CELL); p.yaw=0; p.pitch=-0.12; window.__closeT=performance.now();
          g.allies.forEach((a,i)=>{ if(i) a.model.group.scale.setScalar(0.0001); });
          ['rifle','mg','shotgun'].forEach(t=>g.spawnEnemy(t)); g.enemies.forEach((e,i)=>{ e.pos.set(13.5*g.CELL-1.3+i*1.3,0,8.5*g.CELL-3.4); e.yaw=[0.5,0,-0.6][i]||0; e.react=99; e.cool=99; e.state='guard'; });
          if(g.allies[0]){ const a=g.allies[0]; a.pos.set(13.5*g.CELL+1.6,0,8.5*g.CELL-2.2); }
        })()"""
        await pg.evaluate(setup); await pg.wait_for_timeout(2500); await pg.screenshot(path=f'{shots}/closeup_1.png')
        await pg.evaluate("(()=>{const g=window.__game; g.enemies.forEach(e=>{e.react=0;e.cool=0;});})()"); await pg.wait_for_timeout(1500); await pg.screenshot(path=f'{shots}/closeup_2.png')
        await pg.evaluate("(()=>{const g=window.__game; g.enemies.forEach(e=>{e.hp=1;}); g.player.fireHeld=true;})()"); await pg.wait_for_timeout(2500); await pg.screenshot(path=f'{shots}/closeup_3.png')
        await b.close()
    return errs
check.prep(); pr=check.server()
try: print('errors', asyncio.run(run()))
finally: pr.terminate()
