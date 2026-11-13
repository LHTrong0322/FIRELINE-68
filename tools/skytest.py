"""Chụp cảnh ngoài trời (bầu trời HDRI, sương mù, tia nắng): python3 tools/skytest.py [low|high|ultra]"""
import asyncio, os, sys
sys.argv=[sys.argv[0]]+(sys.argv[1:] or ['high'])
import check
async def run():
    from playwright.async_api import async_playwright
    shots=f'{check.ROOT}/tools/shots'; errs=[]
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome' if os.path.exists('/usr/bin/google-chrome') else None, args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
        ctx=await b.new_context(viewport={'width':960,'height':540}); await ctx.add_init_script(f"try{{localStorage.setItem('tl_quality4', JSON.stringify('{check.Q}'))}}catch(e){{}}")
        pg=await ctx.new_page(); pg.set_default_timeout(300000); pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://127.0.0.1:8799/'); await pg.wait_for_function('window.__gameReady===true', timeout=300000)
        for mp in (os.environ.get('MAPS') or 'khesanh,himlam').split(','):
            await pg.evaluate(f"(async()=>{{ const g=window.__game; g.settings.map='{mp}'; g.settings.mode='base'; await g.startCampaign(); g.player.invuln=9999; }})()")
            await pg.wait_for_timeout(6000)
            for i,(yaw,pitch) in enumerate([(None,0.02),(None,0.22),(2.6,0.05)]):
                await pg.evaluate(f"""(()=>{{const g=window.__game,p=g.player; const s=g.__sunDir||null; let y={yaw if yaw is not None else 'null'};
                  if(y===null){{ const sx=0.555,sz=0.377; y=Math.atan2(-sx,-sz)+0.35; }} p.yaw=y; p.pitch={pitch}; g.enemies.forEach(e=>e.cool=99); }})()""")
                await pg.wait_for_timeout(2500); await pg.screenshot(path=f'{shots}/sky_{mp}_{i}.png')
        await b.close()
    return errs
check.prep(); pr=check.server()
try: print('errors', asyncio.run(run()))
finally: pr.terminate()
