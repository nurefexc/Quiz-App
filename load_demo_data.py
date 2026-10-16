#!/usr/bin/env python3
import os
from datetime import datetime, timedelta
from app import create_app, db
from app.models import User, Quiz, QuestionGroup, Question, Event, Team

def load_demo_data():
    """Load demo data for the quiz application with multiple active and past quizzes"""
    app = create_app()
    
    with app.app_context():
        # Drop all tables and recreate with new schema
        print("Recreating database with new schema...")
        db.drop_all()
        db.create_all()
        
        print("Loading demo data...")
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@quiz.local',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create regular users
        users = []
        for i in range(1, 8):
            user = User(
                username=f'user{i}',
                email=f'user{i}@quiz.local'
            )
            user.set_password('user123')
            users.append(user)
            db.session.add(user)
            
        db.session.flush()
        
        # 1. Active Quiz 1: General Knowledge Challenge
        quiz1 = Quiz(
            title='General Knowledge Challenge',
            description='Test your general knowledge with grouped questions and instant feedback!',
            instant_feedback=True,
            show_score_at_end=True,
            show_correct_answers_at_end=True
        )
        db.session.add(quiz1)
        db.session.flush()

        # Create Question Groups (A and B)
        group_a = QuestionGroup(
            quiz_id=quiz1.id,
            name='Group A - Science & Nature',
            description='Answer the following science questions before moving to Group B.',
            allow_backtrack=True,
            order=0
        )
        group_b = QuestionGroup(
            quiz_id=quiz1.id,
            name='Group B - History & Arts',
            description='Answer history and art questions.',
            allow_backtrack=False,
            order=1
        )
        db.session.add(group_a)
        db.session.add(group_b)
        db.session.flush()
        
        # Questions for Group A
        questions_data_a = [
            {
                'group_id': group_a.id,
                'question_text': 'Which planet is known as the Red Planet?',
                'question_type': 'multiple_choice',
                'option_a': 'Venus',
                'option_b': 'Mars',
                'option_c': 'Jupiter',
                'option_d': 'Saturn',
                'correct_answer': 'b',
                'points': 10
            },
            {
                'group_id': group_a.id,
                'question_text': 'What is the largest ocean on Earth?',
                'question_type': 'multiple_choice',
                'option_a': 'Atlantic Ocean',
                'option_b': 'Indian Ocean',
                'option_c': 'Arctic Ocean',
                'option_d': 'Pacific Ocean',
                'correct_answer': 'd',
                'points': 10
            },
            {
                'group_id': group_a.id,
                'question_text': 'What is the chemical symbol for gold?',
                'question_type': 'multiple_choice',
                'option_a': 'Go',
                'option_b': 'Gd',
                'option_c': 'Au',
                'option_d': 'Ag',
                'correct_answer': 'c',
                'points': 15
            }
        ]
        for idx, q_data in enumerate(questions_data_a):
            q = Question(quiz_id=quiz1.id, order=idx, **q_data)
            db.session.add(q)
            
        # Questions for Group B
        questions_data_b = [
            {
                'group_id': group_b.id,
                'question_text': 'Select all primary colors in standard additive light (RGB):',
                'question_type': 'multiple_select',
                'option_a': 'Red',
                'option_b': 'Green',
                'option_c': 'Blue',
                'option_d': 'Yellow',
                'correct_answer': 'a,b,c',
                'points': 20
            },
            {
                'group_id': group_b.id,
                'question_text': 'Who painted the Mona Lisa?',
                'question_type': 'free_text',
                'correct_answers': 'Leonardo da Vinci\nLeonardo Da Vinci\nDa Vinci\nLeonardo',
                'points': 20,
                'requires_review': False
            }
        ]
        for idx, q_data in enumerate(questions_data_b):
            q = Question(quiz_id=quiz1.id, order=idx+len(questions_data_a), **q_data)
            db.session.add(q)
            
        # Active Event
        active_event = Event(
            name='Autumn Championship 2026',
            description='The premier general knowledge quiz championship for all registered teams.',
            start_time=datetime.now() - timedelta(hours=2),
            end_time=datetime.now() + timedelta(days=2),
            is_active=True,
            quiz_id=quiz1.id
        )
        db.session.add(active_event)
        db.session.flush()
        
        # Teams for Active Event
        team1 = Team(
            name='Brainiacs',
            max_size=5,
            event_id=active_event.id,
            captain_id=users[0].id,  # user1
            score=35
        )
        team2 = Team(
            name='QuizMasters',
            max_size=4,
            event_id=active_event.id,
            captain_id=users[2].id,  # user3
            score=20
        )
        db.session.add(team1)
        db.session.add(team2)
        db.session.flush()
        
        # Assign members (user1 in team1, user2 in team1; user3 in team2, user4 in team2)
        users[0].team_id = team1.id
        users[1].team_id = team1.id
        users[2].team_id = team2.id
        users[3].team_id = team2.id
        
        # 2. Past Quiz 1: Sci-Fi & Pop Culture
        quiz2 = Quiz(
            title='Sci-Fi & Pop Culture 2026',
            description='A retro and modern cinema & sci-fi quiz.',
            instant_feedback=True,
            show_score_at_end=True,
            show_correct_answers_at_end=True
        )
        db.session.add(quiz2)
        db.session.flush()
        
        q_past1 = Question(
            quiz_id=quiz2.id,
            question_text='In "The Matrix", what color pill does Neo take?',
            question_type='multiple_choice',
            option_a='Blue',
            option_b='Red',
            option_c='Green',
            option_d='Yellow',
            correct_answer='b',
            points=10,
            order=0
        )
        q_past2 = Question(
            quiz_id=quiz2.id,
            question_text='What is the name of Han Solo\'s spaceship?',
            question_type='multiple_choice',
            option_a='Enterprise',
            option_b='Millennium Falcon',
            option_c='Serenity',
            option_d='Discovery One',
            correct_answer='b',
            points=10,
            order=1
        )
        db.session.add(q_past1)
        db.session.add(q_past2)
        
        past_event1 = Event(
            name='Summer Sci-Fi Arena 2026',
            description='Pop culture and science fiction showdown concluded in August 2026.',
            start_time=datetime.now() - timedelta(days=60),
            end_time=datetime.now() - timedelta(days=45),
            is_active=False,
            quiz_id=quiz2.id
        )
        db.session.add(past_event1)
        db.session.flush()
        
        team_past1 = Team(
            name='CyberPunks',
            max_size=5,
            event_id=past_event1.id,
            score=85
        )
        team_past2 = Team(
            name='StarGazers',
            max_size=5,
            event_id=past_event1.id,
            score=70
        )
        db.session.add(team_past1)
        db.session.add(team_past2)
        
        # 3. Past Quiz 2: Geography & World Wonders
        quiz3 = Quiz(
            title='World Wonders & Geography',
            description='Exploring capitals, continents, and ancient monuments.',
            instant_feedback=False,
            show_score_at_end=True,
            show_correct_answers_at_end=True
        )
        db.session.add(quiz3)
        db.session.flush()
        
        q_geo = Question(
            quiz_id=quiz3.id,
            question_text='What is the capital of Australia?',
            question_type='multiple_choice',
            option_a='Sydney',
            option_b='Melbourne',
            option_c='Canberra',
            option_d='Brisbane',
            correct_answer='c',
            points=15,
            order=0
        )
        db.session.add(q_geo)
        
        past_event2 = Event(
            name='Global Geography Masters',
            description='International geography quiz concluded in July 2026.',
            start_time=datetime.now() - timedelta(days=90),
            end_time=datetime.now() - timedelta(days=75),
            is_active=False,
            quiz_id=quiz3.id
        )
        db.session.add(past_event2)
        db.session.flush()
        
        team_geo1 = Team(
            name='Globetrotters',
            max_size=5,
            event_id=past_event2.id,
            score=95
        )
        team_geo2 = Team(
            name='MapExplorers',
            max_size=5,
            event_id=past_event2.id,
            score=60
        )
        db.session.add(team_geo1)
        db.session.add(team_geo2)
        
        db.session.commit()
        print("Demo data loaded successfully!")
        print("\nCreated Users:")
        print("  - Admin: admin / admin123 (Full admin privileges)")
        print("  - User 1: user1 / user123 (Team Captain of Brainiacs)")
        print("  - User 2: user2 / user123 (Member of Brainiacs)")
        print("  - User 3: user3 / user123 (Team Captain of QuizMasters)")
        print("  - User 4: user4 / user123 (Member of QuizMasters)")
        print("  - User 5..7: user5..7 / user123 (Free users ready to create/join teams)")
        print("\nActive Events:")
        print(f"  - {active_event.name} (ID: {active_event.id})")
        print("\nPast Events:")
        print(f"  - {past_event1.name} (Winner: CyberPunks)")
        print(f"  - {past_event2.name} (Winner: Globetrotters)")

if __name__ == '__main__':
    load_demo_data()
