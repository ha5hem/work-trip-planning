---
name: business-trip-planning
description: Plan a business trip from Vancouver. Use when the user mentions an upcoming trip, conference or event in another city, or asks for flight options or travel dates. Covers setting dates, flight options, the booking-request email draft to Dave, and the trip record.
---

# Business trip planning

## Traveller profile
- Home airport: Vancouver (YVR), Pacific Time.
- Preferred airline: Air Canada, nonstop where available.
- Has 2 young kids, so every night away matters. Hard cap: 3 nights away; fewer if there was a trip the week before.
- Uses trips to meet business contacts and personal network in the destination city.

## Algorithm: setting dates
1. **Get the event times.** Confirm each attendance block with date, start/end time and timezone. Check that weekday and date match (e.g. "Monday the 24th"), and flag any mismatch.
2. **Ask how many nights the user wants to stay.** Do this before proposing anything. Mention relevant context, such as a trip the prior week or the 3-night cap.
3. **Brainstorm date/flight combinations** that fit that number of nights. Maximize usable time on site (event, plus meetings with contacts) and minimize **evenings away from home**. A red-eye counts as an evening away.
   - Outbound: the latest flight that still lands with a safe buffer before the first session. Aim for 3+ hours after landing; consider weather and season.
   - Return: the earliest flight after the last session, leaving time to get to the airport. Allow about 2 hours from venue to departure for domestic flights, more for international.
   - For each combination, show: flights (number, depart/arrive local), hotel nights, evenings away, the leave-home and back-home times, and the free windows for meetings.
4. **Recommend one option** and say what the alternative buys (e.g. "+1 night = a full afternoon for meetings").
5. Once the user picks, update the trip record.
6. **Draft the booking request** for Dave (see below).

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

## Trip record
Keep one file per trip at `trips/YYYY-MM-<city>.md` with:
- Event: name, venue, attendance blocks (local time)
- Constraints: night cap, the context behind it
- Flights considered / chosen (with status: proposed / booked + confirmation #)
- Hotel
- Contacts to meet: name, purpose, slot, status
- Open to-dos
