<p align="center">
    <img src="https://raw.githubusercontent.com/techtanic/Discounted-Udemy-Course-Enroller/refs/heads/master/extra/promo.gif">
    <br/>
    <img src="https://forthebadge.com/images/badges/made-with-python.svg">
    <br/>
    <a href="https://github.com/techtanic/Discounted-Udemy-Course-Enroller/graphs/commit-activity"><img alt="Maintenance" src="https://img.shields.io/badge/Maintained%3F-yes-green.svg?style=for-the-badge"></a>
    <a target="_blank" href="https://discord.gg/wFsfhJh4Rh"><img alt="Discord" src="https://img.shields.io/discord/703266580846346361.svg?label=Discord&logo=Discord&colorB=7289da&style=for-the-badge"></a>
    <br/>
    <a href="https://github.com/techtanic/Discounted-Udemy-Course-Enroller"><img src="https://cdn.discordapp.com/attachments/823472016999972884/841661124410736710/standard_13.gif"></a>
</p>

# Discounted Udemy Course Enroller

> Software to enroll in available Udemy Paid/Free courses having coupons automatically to your Udemy account.

Everything you need can be on the website: https://techtanic.github.io/duce/

## Key Features

- Beautiful GUI
- One click login using Browser cookies.(Supports major browsers)
- One click to add all available courses with coupons to your udemy account
- Uses popular sites for coupons
- Many more features
- CLI version available for automation
- Advanced filters

## Run from source

```sh
pip install -r requirements.txt
python gui.py        # GUI
python cli.py        # terminal interface
```

On Windows you can double-click `run-gui.bat` / `run-cli.bat` instead of the
`.py` files (keeps the console open if something fails).

## Automatic daily runs

- **Local (enrollment):** the CLI runs fully unattended when settings have
  `use_browser_cookies: true` (or saved email/password). Create a scheduled
  task with `taskschd.msc` → "Create Basic Task" → Daily → "Start a program" →
  point it at `run-cli-auto.bat`. Your browser must be logged in to Udemy (the
  cookies are read from disk, so the browser can be closed).
- **Monitoring (read-only):** GitHub Actions runs the scraper smoke test
  (`tests/smoke_all.py`) daily at 06:00 UTC. It never commits anything - if a
  coupon site changes its HTML, it only opens an issue so you can fix the
  scraper. Unit tests run on every push/PR.
- **Dead coupons:** coupons confirmed dead are cached for 24 hours
  (`duce-dead-coupons.json`) so runs skip re-validating them. The cache is
  keyed by course + coupon code, so a re-issued code is always checked fresh,
  and entries expire automatically.

# Downloads

<table>
<thead >
  <tr>
    <th style="text-align: center">GUI</th>
    <th style="text-align: center">CLI</th>
  </tr>
</thead>
<tbody>
  <tr align="center">
    <td><a href="https://github.com/techtanic/Discounted-Udemy-Course-Enroller/releases/latest/download/DUCE-GUI-windows.exe">
         <img alt="GUI Windows exe" src="https://img.shields.io/static/v1?message=Download&logo=windows&labelColor=5c5c5c&color=1182c3&label=%20&style=for-the-badge"
         >
      </a></td>
    <td><a href="https://github.com/techtanic/Discounted-Udemy-Course-Enroller/releases/latest/download/DUCE-CLI-windows.exe">
         <img alt="CLI Windows exe" src="https://img.shields.io/static/v1?message=Download&logo=windows&labelColor=5c5c5c&color=1182c3&label=%20&style=for-the-badge">
      </a></td>
    
  </tr>
</tbody>
</table>

<h2><details>
<summary>Screenshots of GUI</summary>

![Login](/extra/gui-login.png)

![Discounted Udemy Course Enroller](/extra/gui-main.png)

![Coupon Scraping](/extra/gui-scraping.png)

![Enrolling](/extra/gui-enrolling.png)

</details>

## Disclaimer

![](/extra/disclaimer.png)

## Donate

BTC `bc1qdyjwj0eqxjk5hxejah4gyclrumwtqs3hqp63uz`

BTC `14JNjiNoiKcbCHcxcqUxgJcVgyDfhGbxQF`


<center>
Made with ❤️
</center>