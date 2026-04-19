# UML Diagrams (source)

The diagrams in the phase-1 PDF were generated from the PlantUML source
below. You can re-render them at <https://www.plantuml.com/plantuml/> or
via any local PlantUML install.

---

## 1. Component diagram

```plantuml
@startuml
skinparam backgroundColor #F4F1EC
skinparam componentStyle rectangle

actor User
node "Browser" as Browser {
  [HTML / CSS]
  [chat.js (fetch)]
}
node "Flask server (app.py)" as Server {
  [POST /chat]
  [POST /reset]
  [GET  /bookings]
}
package "HotelBookingBot" {
  [Dialog Manager\n(chatbot.py)]      as DM
  [Intent Classifier\n(nlp.py)]       as IC
  [Entity Extractors\n(nlp.py)]       as EE
  [Booking State\n(booking.py)]       as BS
  database "bookings.json" as DB
}

User --> Browser
Browser --> Server : JSON
Server  --> DM
DM --> IC : classify(text)
DM --> EE : extract_*()
DM --> BS : fill slot
BS --> DB : persist on confirm
@enduml
```

## 2. Sequence diagram (happy-path booking)

```plantuml
@startuml
skinparam backgroundColor #F4F1EC
actor User
participant "Chat UI" as UI
participant "Flask\n(app.py)" as F
participant "HotelBookingBot\n(chatbot.py)" as B
participant "IntentClassifier" as IC
participant "Entity extractors" as EE
participant "BookingStore" as DB

User -> UI : "book a room"
UI -> F  : POST /chat
F -> B   : respond("book a room")
B -> IC  : classify()
IC --> B : ("book_room", 0.8)
B --> F  : "Can I have your name?"
F --> UI : 200 JSON
UI --> User : bubble

User -> UI : "Jane Doe"
UI -> F : POST /chat
F -> B  : respond("Jane Doe")
B -> EE : extract_name()
EE --> B : "Jane Doe"
B --> F  : "What dates?"
...
User -> UI : "yes confirm"
UI -> F : POST /chat
F -> B  : respond("yes confirm")
B -> DB : save(booking)
DB --> B : "AGH-…"
B --> F  : "Confirmed! AGH-…"
F --> UI : 200 JSON
UI --> User : bubble
@enduml
```

## 3. State diagram (dialog slots)

```plantuml
@startuml
skinparam backgroundColor #F4F1EC

[*] --> greet
greet    --> name      : greet / book_room
name     --> dates     : name filled
dates    --> guests    : dates filled
guests   --> breakfast : guests filled
breakfast --> payment  : breakfast filled
payment  --> confirm   : payment filled
confirm  --> [*]       : confirm_yes
confirm  --> name      : confirm_no / restart
greet    --> [*]       : goodbye
@enduml
```
