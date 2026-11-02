---
name: business-trip-planning
description: Plan a business trip from Vancouver. Use when the user mentions an upcoming trip, conference or event in another city, or asks for flight options or travel dates. Covers setting dates from the calendar, flight options, the flight booking-request email draft to Dave, the hotel search and hotel email, calendar management (flights, travel blocks, labels, declining conflicts, partner meeting placeholders), and the trip record.
---

# Business trip planning

## Traveller profile
- Home airport: Vancouver (YVR), Pacific Time.
- Preferred airline: Air Canada, nonstop where available.
- Has 2 young kids, so every night away matters. Hard cap: 3 nights away; fewer if there was a trip the week before.
- Uses trips to meet business contacts and personal network in the destination city.

## Algorithm: setting dates
1. **Get the event times.** Check the user's Google Calendar first for the trip's events, dates and venue addresses. Confirm each attendance block with date, start/end time and timezone. Check that weekday and date match (e.g. "Monday the 24th"), and flag any mismatch.
2. **Ask how many nights the user wants to stay.** Do this before proposing anything. Mention relevant context, such as a trip the prior week or the 3-night cap.
3. **Brainstorm date/flight combinations** that fit that number of nights. Maximize usable time on site (event, plus meetings with contacts) and minimize **evenings away from home**. A red-eye counts as an evening away.
   - Outbound: the latest flight that still lands with a safe buffer before the first session. Aim for 3+ hours after landing; consider weather and season.
   - Return: the earliest flight after the last session, leaving time to get to the airport. Allow about 2 hours from venue to departure for domestic flights, more for international.
   - For each combination, show: flights (number, depart/arrive local), hotel nights, evenings away, the leave-home and back-home times, and the free windows for meetings.
4. **Recommend one option** and say what the alternative buys (e.g. "+1 night = a full afternoon for meetings").
5. Once the user picks, update the trip record.
6. **Draft the booking request** for Dave (see below).
7. **Find a hotel** (see below).
8. **Manage the calendar** once flights are booked (see Calendar management).

## Flight lookup
- Look for Air Canada nonstop schedules for the exact dates. Note the season, since schedules change around late October and late March.
- If aircanada.com or other schedule sites are blocked in the session, use web search. Say that the times come from aggregators and must be confirmed on aircanada.com.

## Booking request
Dave (David Gens) books travel. Once flights are chosen, create a Gmail draft asking him to book them:
- Use the Gmail connector's `create_draft` with `includeSignature: true`. If no connector is available, compose the draft in Gmail through the browser.
- To: David Gens <dgens@merchantgrowth.com> and Paige Stefanyshyn <pstefanyshyn@merchantgrowth.com>.
- Subject: `Please book: <route> business, <dates> (<city>)`.
- Body: keep it short and follow this template (Montreal, Nov 2026):

  ```
  Hi Dave & Paige,
  Could you please book these Air Canada flights for my trip to <event> in <city>. My Aeroplan number is 585 22 540. Just let me know if you'd rather I book and expense.
  Outbound: <Weekday, Month D>
  <flight>, <City> (<IATA>) <HH:MM> → <City> (<IATA>) <HH:MM>
  Return: <Weekday, Month D>
  <flight>, <City> (<IATA>) <HH:MM> → <City> (<IATA>) <HH:MM>
  When I checked on <date>, the round trip in Business Standard came to about $<total> CAD ($<out> out, $<back> back). Latitude, which is refundable with no change fees, was about $<total>. Standard is fine unless you think Latitude is worth the difference.
  <Only if seats are low: "<flight> had only N business seats left, so please book it soon if you can.">
  If you could pls confirm once it's done.
  Thanks,
  ```
  End at "Thanks," (the signature carries the name). Don't add a hotel request unless the user asks.
- Never send it. Leave it as a draft, give the user its link, and mark the flights "requested from Dave" in the trip record.

## Hotel search
1. **Check the calendar for dates and locations.** Pull every in-person event on the trip (conference, dinners, meetings) with its venue address. Stay nights = arrival night through the night before the return flight. Flag calendar entries whose timezone looks wrong (e.g. an evening event in the destination entered in Pacific time).
2. **Look up options** (Google Hotels in the browser works well; use the exact check-in/check-out dates). Rank by, in order:
   - **Location:** closest to the venues. The user prefers being able to walk to every event when possible; otherwise central downtown or a nice, convenient neighbourhood. Weigh early-morning sessions and season (e.g. indoor/underground connections in winter). Give walk or taxi minutes to each venue.
   - **Reviews:** rating and review count.
   - **Availability:** rooms bookable for the exact dates. Drop hotels with no online rates, or say "call to book".
   - **Cost:** last. Merchant Growth stays at nice hotels (4–5 star), so don't trade quality for price.
3. **Share a lower-, mid- and higher-priced option** from the best-located, best-reviewed set: hotel, area, minutes to each venue, rating (count), nightly rate (CAD, and the date checked), and one line on why. Recommend one. Add the shortlist to the trip record.
4. **Once the user narrows it down, draft the hotel email** (Gmail connector `create_draft`, `includeSignature: true`, to Dave and Paige; never send):

   ```
   Hi Dave & Paige,
   What's our usual approach for booking hotels? I've narrowed it down to <N> options for my <city> trip, staying <N> nights: check in <Weekday, Month D>, check out <Weekday, Month D>.
   <Hotel>: about $<rate>/night. <One line on why.>
   <Hotel>: about $<rate>/night. <One line on why.>
   Both had rooms available for those dates when I checked on <date>. Prices are the lowest nightly rate shown, in CAD.
   Paige, could you please help book whichever one fits our approach?
   Thanks,
   ```

## Calendar management
Do this once the booking confirmation arrives. Use the Google Calendar connector; set `notificationLevel: NONE` on edits to solo events.

### 1. Read the booking
Pull flight numbers, local times, cabin, booking reference and seat status from the Air Canada confirmation in Gmail (search `from:aircanada`). Use the confirmation, not the trip record, as the source of truth; flag any difference (e.g. a cabin other than the one requested).

### 2. Get time zones right
- Create each event with an explicit IANA `timeZone`: `America/Vancouver` for BC, `America/Toronto` for Montreal/Toronto.
- Check the offset against the flight duration before trusting it. BC is on UTC−7 year-round in this calendar, so in winter Vancouver is **2 h** behind Eastern, not 3 (AC304: 10:20 PT + 4h44 = 17:04 ET).
- A flight spans two zones: start and end must be in one zone, so convert the arrival into the departure zone.
- Check existing trip events (dinners, conferences) for entries made in the wrong zone and fix them with the user's OK.

### 3. Add travel blocks
For each flight, add:
1. **Travel to <airport>**: from the origin to the airport, ending at check-in.
2. **Check-in: <flight>**: 1 hour before departure.
3. **✈ <flight> <from>→<to> (dep HH:MM TZ, arr HH:MM TZ)**: departure to arrival. Put the aircraft, cabin, booking reference, ticket number and seat status in the description.
4. **Travel from <airport>**: arrival + ~20 min to deplane and reach the curb, plus the ground leg.

Ground-leg rules:
- **Daytime:** take the airport train where one exists (Toronto: UP Express). Montreal has no airport train until the REM station opens (expected late 2027), so use Uber there.
- **Early morning, late night, or no practical train:** Uber.
- **Home:** West Vancouver. There's no practical train to YVR, so use Uber. Ask for the exact address if needed; never write it into calendar events or this repo.
- Get times from Google Maps directions with **Arrive by** / **Depart at** set to the exact day and time; type addresses into the fields, don't put them in the URL. Use the upper end of the "typically X–Y min" range and note the range in the description.

### 4. Colour and label
Labels are tied to the standard event colours (`colorId`):

| Label | Colour | colorId | Use for |
|---|---|---|---|
| Travel | Graphite | 8 | Flights, Ubers, check-ins, hotel downtime, check-out |
| Partner Meetings | Blueberry | 9 | Partner dinners, breakfasts, coffees, placeholders |
| Conferences & Events | Lavender | 1 | Conferences, event dinners, forums (include duplicate copies from registration invites) |
| 1:1's | Tangerine | 6 | (existing) |

Don't use Sage (2), which is reserved for something else. The connector can only set the 11 standard colours.

### 5. Clear conflicting meetings
List every event from the first travel block to the last, then:
- **Recurring meetings organized by others:** decline that instance only (`respond_to_event`, `declined`, no comment).
- **Recurring meetings the user organizes:** these can't be declined, only cancelled. List them and ask first; on a yes, cancel that instance only, with attendees notified.
- **Solo blocks** (prep, lunch, focus): leave them.
- Report what was declined and cancelled, and suggest the user follow up with anyone whose 1:1 was cancelled.

### 6. Add meeting placeholders
Fill the remaining on-site time with `[Placeholder] Partner <Dinner|Breakfast|Coffee / Office Meeting> – TBD` blocks (Partner Meetings colour, busy, no guests). Framework:
- **Dinner:** ~5:30–7:30 PM.
- **Breakfast:** ~8:00–9:30 AM.
- **Daytime coffee/office:** 1 hr between 9 AM and 5 PM, with 30 min between meetings.

Judgement on filler time (Travel colour):
- After a conference ends, block ~1 hr of **hotel downtime** before dinner.
- On departure day, block time to **get back to the hotel, pack and check out** before the airport Uber. Keep the last meeting close to the hotel.
- Skip any slot that collides with flights, the event or an existing dinner, and say why.

### 7. Record it
Add the travel schedule, the meeting windows, the placeholders and what was declined/cancelled to the trip record.

## Trip record
Keep one file per trip at `trips/YYYY-MM-<city>.md` with:
- Event: name, venue, attendance blocks (local time)
- Constraints: night cap, the context behind it
- Flights considered / chosen (with status: proposed / booked + confirmation #)
- Hotel
- Contacts to meet: name, purpose, slot, status
- Open to-dos
