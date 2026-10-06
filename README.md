# 🏏 Sunday Cricket Team Balancer

A cricket team balancing application designed for recurring
Sunday cricket sessions.

The application balances teams based on:

- Batting ability
- Bowling ability
- Fielding ability
- Player roles
- Overall player strength
- Elite player distribution
- Strong player distribution
- Previous team assignments

It also attempts to minimize unnecessary reshuffling between
matches.

---

## Project Structure

```text
cricket_team_balancer/
│
├── app.py
│
├── backend/
│   ├── __init__.py
│   ├── team_balancer.py
│   ├── session_manager.py
│   ├── player_service.py
│   └── models.py
│
├── config.py
├── players.csv
├── requirements.txt
└── README.md