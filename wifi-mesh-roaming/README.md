# wifi-mesh-roaming

Values in capitals (MY_WIFI, DECO1_5GHZ_BSSID, LAPTOP_IP, ETH_ADAPTER, ...) are placeholders: put in your own Wi-Fi profile name, access point BSSIDs, addresses and interface name.

Fixes Teams calls that drop or freeze while Wi-Fi still shows "connected". The laptop sat between two
Deco mesh units and kept switching between them. Contains a read-only check script and the fix.

## The problem (diagnosed 2026-10-14)

Laptop: ASUS Vivobook S16, Intel Wi-Fi 6E AX211 (`iwlwifi`), NetworkManager 1.46, Wi-Fi `MY_WIFI`.

- Two Deco units reach the desk with the **same 5 GHz signal**, about -66 dBm (`DECO1_5GHZ_BSSID` and
  `DECO2_5GHZ_BSSID`, both on channel 40). When neither is clearly better, `wpa_supplicant` switches
  (roams) back and forth, sometimes every 1–2 minutes. Sometimes it also switches to 2.4 GHz.
- Every roam makes NetworkManager restart DHCP. Usually the router answers within milliseconds. A few
  times a day it does not, and NetworkManager **removes the IPv4 address** for about 15–35 seconds.
  During that time the Wi-Fi icon still shows "connected", but no traffic gets through. A Teams call
  cannot survive that.

Measured with `wifi-roam-check` (one row per boot; the date is the boot's last log entry):

| Boot ended | Roams | IPv4 address losses |
|---|---|---|
| 2026-10-04 | 192 | 4 |
| 2026-10-05 | 52 | 1 |
| 2026-10-07 | 87 | 3 |
| 2026-10-09 | 83 | 2 |
| 2026-10-13 | 39 | 2 |
| 2026-10-14 | 29 | 3 |

The 2026-10-14 row includes one loss caused on purpose: the reconnect at 11:29:55 that applied the fix.
"Roams" counts both planned switches (`disconnect from AP … for new auth`) and dropped links
(`Connection to AP … lost`).

A typical outage, 2026-10-14 (from `journalctl`):

```
11:28:10  Connection to AP DECO2_24GHZ_BSSID lost          (the 2.4 GHz radio)
11:28:13  DECO1_5GHZ_BSSID rejected association temporarily; comeback 1024 ms
11:28:14  associated; NetworkManager restarts DHCP
11:28:29  DHCP: no lease  ->  IPv4 address LAPTOP_IP removed
11:28:48  DHCP: new lease ->  address back                  (about 35 s without network)
```

Packet loss over 30 s, during the bad period (before the fix): **55% to the router, 90% to 1.1.1.1.**

## The fix

Lock the Wi-Fi profile to one 5 GHz access point, so there is nothing to switch to:

```bash
nmcli con modify MY_WIFI 802-11-wireless.band a 802-11-wireless.bssid DECO1_5GHZ_BSSID
nmcli con up MY_WIFI
```

IPv6 is disabled as well, on Wi-Fi and on both wired profiles:

```bash
for c in MY_WIFI "Wired connection 1" "Wired connection 2"; do nmcli con modify "$c" ipv6.method disabled; done
nmcli con up MY_WIFI
```

The Deco network gives no global IPv6 address, only a link-local one and a default IPv6 route. So no
traffic used IPv6. Disabling it removes that useless route and the DHCPv6 restart on every reconnect.
It does not change the roaming itself; the BSSID lock does that.

Result after the fix: **0% loss to the router and to 1.1.1.1 over 3 minutes, 0 roams.** Again 0% over
30 s after IPv6 was disabled. `teams.microsoft.com`, `teams.cloud.microsoft` and
`login.microsoftonline.com` answer over IPv4 in 0.15–0.3 s.

Wi-Fi power saving was already off (`wifi.powersave = 2` in
`/etc/NetworkManager/conf.d/default-wifi-powersave-on.conf`), so it was not the cause.

## The catch: the lock is tied to one Deco unit

With the BSSID locked, the profile **only** connects to that one access point. If you work in another
room, or that Deco unit is off or moved, Wi-Fi will not connect. Undo:

```bash
nmcli con modify MY_WIFI 802-11-wireless.bssid "" 802-11-wireless.band ""
nmcli con up MY_WIFI
```

To enable IPv6 again:

```bash
for c in MY_WIFI "Wired connection 1" "Wired connection 2"; do nmcli con modify "$c" ipv6.method auto; done
```

A better fix for a desk: an Ethernet cable. The USB Ethernet adapter (`ETH_ADAPTER`) already has a
profile. When a cable is connected, NetworkManager prefers it over Wi-Fi (route metric 100 versus 600).

## Check script

```bash
./wifi-roam-check            # last 6 boots, 30 s ping test
./wifi-roam-check 2 10       # last 2 boots, 10 s ping test
```

It prints the current access point and any band/BSSID lock, the access points visible for the SSID,
roams and IPv4 address losses per boot, and packet loss to the router and to 1.1.1.1. It changes
nothing. It needs `nmcli`, `journalctl` and `ping`; no root.

With a BSSID lock in place, the list may show only the locked 5 GHz access point plus the 2.4 GHz ones (seen 2026-10-14).
That is expected.
