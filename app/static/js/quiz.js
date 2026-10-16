// Quiz Application - Custom Standalone JavaScript (No External Dependencies)
(function() {
    'use strict';

    document.addEventListener('DOMContentLoaded', function() {
        initNavbar();
        initDropdowns();
        initAlerts();
        initQuizOptions();
        initQuizProgress();
        initDynamicQuizEngine();
    });

    // 1. Mobile Navbar Toggle
    function initNavbar() {
        const togglers = document.querySelectorAll('.navbar-toggler, [data-bs-toggle="collapse"]');
        togglers.forEach(function(toggler) {
            toggler.addEventListener('click', function(e) {
                e.preventDefault();
                const targetSelector = toggler.getAttribute('data-bs-target') || '#navbarNav';
                const target = document.querySelector(targetSelector);
                if (target) {
                    const isExpanded = target.classList.toggle('show');
                    toggler.setAttribute('aria-expanded', isExpanded ? 'true' : 'false');
                }
            });
        });

        // Close mobile navbar when resizing back to desktop screen
        window.addEventListener('resize', function() {
            if (window.innerWidth >= 992) {
                const navbars = document.querySelectorAll('.navbar-collapse.show');
                navbars.forEach(function(nav) {
                    nav.classList.remove('show');
                });
            }
        });
    }

    // 2. Dropdown Menus (e.g. Language Selector)
    function initDropdowns() {
        const dropdownToggles = document.querySelectorAll('.dropdown-toggle, [data-bs-toggle="dropdown"]');
        dropdownToggles.forEach(function(toggle) {
            toggle.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const parent = toggle.closest('.dropdown');
                const menu = parent ? parent.querySelector('.dropdown-menu') : null;
                
                // Close other open dropdowns
                document.querySelectorAll('.dropdown-menu.show').forEach(function(openMenu) {
                    if (openMenu !== menu) {
                        openMenu.classList.remove('show');
                    }
                });

                if (menu) {
                    menu.classList.toggle('show');
                }
            });
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.dropdown')) {
                document.querySelectorAll('.dropdown-menu.show').forEach(function(menu) {
                    menu.classList.remove('show');
                });
            }
        });
    }

    // 3. Dismissible Alerts
    function initAlerts() {
        const alertCloseButtons = document.querySelectorAll('.alert .btn-close, [data-bs-dismiss="alert"]');
        alertCloseButtons.forEach(function(btn) {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                const alert = btn.closest('.alert');
                if (alert) {
                    alert.style.transition = 'opacity 0.25s ease, transform 0.25s ease, max-height 0.25s ease, margin 0.25s ease, padding 0.25s ease';
                    alert.style.opacity = '0';
                    alert.style.transform = 'translateY(-8px)';
                    setTimeout(function() {
                        alert.remove();
                    }, 250);
                }
            });
        });
    }

    // 4. Quiz Options (Radio & Checkbox selections)
    function initQuizOptions() {
        const quizOptions = document.querySelectorAll('.quiz-option');
        if (!quizOptions.length) return;

        quizOptions.forEach(function(option) {
            bindOptionEvents(option);
        });

        const textareas = document.querySelectorAll('.question-card textarea');
        textareas.forEach(function(textarea) {
            textarea.addEventListener('input', updateProgressBar);
        });
    }

    function bindOptionEvents(option) {
        const input = option.querySelector('input');
        if (!input) return;

        if (input.checked) {
            option.classList.add('selected');
        }

        option.addEventListener('click', function(e) {
            if (e.target !== input) {
                input.checked = input.type === 'radio' ? true : !input.checked;
                input.dispatchEvent(new Event('change', { bubbles: true }));
            }
        });

        input.addEventListener('change', function() {
            const card = option.closest('.question-card');
            if (card && input.type === 'radio') {
                card.querySelectorAll('.quiz-option').forEach(function(opt) {
                    opt.classList.remove('selected');
                });
            }
            if (input.checked) {
                option.classList.add('selected');
            } else {
                option.classList.remove('selected');
            }
            updateProgressBar();
        });
    }

    // 5. Quiz Progress Tracker
    function initQuizProgress() {
        const container = document.querySelector('.quiz-progress-container');
        if (container) {
            updateProgressBar();
        }
    }

    function updateProgressBar() {
        const questionCards = document.querySelectorAll('.question-card');
        if (!questionCards.length) return;

        let answeredCount = 0;
        questionCards.forEach(function(card) {
            const isSubmitted = card.classList.contains('is-answered');
            const checkedInputs = card.querySelectorAll('input:checked');
            const textarea = card.querySelector('textarea');
            const hasAnswer = isSubmitted || (checkedInputs.length > 0) || (textarea && textarea.value.trim().length > 0);
            if (hasAnswer) {
                answeredCount++;
            }
        });

        const progressBar = document.getElementById('quiz-progress-bar');
        const progressText = document.getElementById('quiz-progress-text');
        if (progressBar && progressText) {
            const percent = Math.round((answeredCount / questionCards.length) * 100);
            progressBar.style.width = percent + '%';
            const i18nAnswered = (window.QUIZ_CONFIG && window.QUIZ_CONFIG.i18n && window.QUIZ_CONFIG.i18n.answered) ? window.QUIZ_CONFIG.i18n.answered : 'answered';
            progressText.textContent = answeredCount + '/' + questionCards.length + ' ' + i18nAnswered;
        }
    }

    // 6. Dynamic API-Driven Quiz Engine with Group/Page Navigation
    function initDynamicQuizEngine() {
        const container = document.getElementById('quiz-app-container');
        if (!container || !window.QUIZ_CONFIG) return;

        const eventId = window.QUIZ_CONFIG.eventId;
        const i18n = window.QUIZ_CONFIG.i18n || {};

        let quizState = {
            quiz: {},
            event: {},
            team: {},
            groups: [],
            currentGroupIndex: 0,
            highestGroupIndex: 0,
            allQuestions: [],
            userAnswers: {},
            isCompleted: false
        };

        // Fetch Initial Data via API
        fetch('/api/events/' + eventId + '/quiz')
            .then(function(res) {
                if (!res.ok) {
                    return res.json().then(function(err) { throw new Error(err.error || 'Failed to load quiz'); });
                }
                return res.json();
            })
            .then(function(data) {
                document.getElementById('quiz-loading-spinner').style.display = 'none';
                
                quizState.quiz = data.quiz;
                quizState.event = data.event;
                quizState.team = data.team;
                quizState.groups = data.groups;
                quizState.isCompleted = data.attempt.is_completed;
                quizState.currentGroupIndex = data.attempt.current_group_index || 0;
                quizState.highestGroupIndex = data.attempt.highest_group_index || 0;

                // Flatten questions & record answers
                data.groups.forEach(function(g) {
                    g.questions.forEach(function(q) {
                        quizState.allQuestions.push(q);
                        if (q.answered) {
                            quizState.userAnswers[q.id] = {
                                selected_answer: q.user_answer,
                                is_correct: q.is_correct,
                                points_earned: q.points_earned,
                                is_reviewed: q.is_reviewed
                            };
                        }
                    });
                });

                if (quizState.isCompleted) {
                    window.location.href = window.QUIZ_CONFIG.resultsUrl;
                    return;
                }

                // Make sure currentGroupIndex is in valid range
                if (quizState.currentGroupIndex >= quizState.groups.length) {
                    quizState.currentGroupIndex = quizState.groups.length - 1;
                }
                if (quizState.currentGroupIndex < 0) {
                    quizState.currentGroupIndex = 0;
                }

                renderQuizView();
            })
            .catch(function(err) {
                console.error(err);
                const spinner = document.getElementById('quiz-loading-spinner');
                if (spinner) {
                    spinner.innerHTML = '<div class="alert alert-danger">' + escapeHtml(err.message) + '</div>';
                }
            });

        function renderQuizView() {
            const navControls = document.getElementById('quiz-nav-controls');
            if (navControls) {
                navControls.style.removeProperty('display');
                navControls.style.display = 'flex';
            }

            renderCurrentGroup();
            updateNavigationButtons();
            updateHeaderAndProgress();
        }

        function renderCurrentGroup() {
            const groupListEl = document.getElementById('group-questions-list');
            if (!groupListEl) return;
            groupListEl.innerHTML = '';

            const currentGroup = quizState.groups[quizState.currentGroupIndex];
            if (!currentGroup) return;

            if (currentGroup.description) {
                const descEl = document.createElement('div');
                descEl.className = 'alert alert-info mb-4 bg-black bg-opacity-25 border-info border-opacity-50 text-secondary';
                descEl.innerHTML = '<p class="mb-0">' + escapeHtml(currentGroup.description) + '</p>';
                groupListEl.appendChild(descEl);
            }

            currentGroup.questions.forEach(function(q, idx) {
                const questionCard = buildQuestionCard(q, idx);
                groupListEl.appendChild(questionCard);
            });

            // Re-bind option click handlers
            groupListEl.querySelectorAll('.quiz-option').forEach(function(opt) {
                bindOptionEvents(opt);
            });

            // Bind submit handlers
            groupListEl.querySelectorAll('.question-submit-form').forEach(function(form) {
                form.addEventListener('submit', function(e) {
                    e.preventDefault();
                    handleAnswerSubmit(form);
                });
            });

            updateHeaderAndProgress();
        }

        function buildQuestionCard(q, idx) {
            const card = document.createElement('div');
            card.className = 'card question-card mb-4' + (q.answered ? ' is-answered' : '');
            card.dataset.questionId = q.id;

            let typeBadge = '';
            if (q.question_type === 'free_text') {
                typeBadge = '<span class="badge bg-info">' + escapeHtml(i18n.freeText || 'Free Text') + '</span>';
            } else if (q.question_type === 'multiple_select') {
                typeBadge = '<span class="badge bg-warning text-dark">' + escapeHtml(i18n.multipleSelect || 'Multiple Select') + '</span>';
            }

            let statusBadge = '';
            if (q.answered) {
                if (quizState.quiz.instant_feedback) {
                    if (!q.is_reviewed) {
                        statusBadge = '<span class="badge bg-warning text-dark">' + escapeHtml(i18n.underReview || 'Under Review') + '</span>';
                    } else if (q.is_correct) {
                        statusBadge = '<span class="badge bg-success">' + escapeHtml(i18n.correct || 'Correct') + ' (+' + (q.points_earned || 0) + ' pts)</span>';
                    } else {
                        statusBadge = '<span class="badge bg-danger">' + escapeHtml(i18n.incorrect || 'Incorrect') + ' (0 pts)</span>';
                    }
                } else {
                    statusBadge = '<span class="badge bg-primary">' + escapeHtml(i18n.answerSaved || 'Answer saved') + '</span>';
                }
            }

            let cardBodyContent = '';
            if (q.answered) {
                cardBodyContent = `
                    <div class="p-3 rounded bg-black bg-opacity-25 border border-secondary border-opacity-25">
                        <span class="text-secondary small d-block mb-1">${escapeHtml(i18n.yourAnswer || 'Your Answer')}:</span>
                        <strong class="text-light fs-6">${escapeHtml(q.user_answer || '')}</strong>
                    </div>
                `;
            } else {
                cardBodyContent = `
                    <form class="question-submit-form" data-question-id="${q.id}">
                        <input type="hidden" name="question_id" value="${q.id}">
                        ${buildQuestionInputHTML(q)}
                        <div class="d-flex align-items-center gap-2 mt-3">
                            <button type="submit" class="btn btn-primary px-4 btn-submit-q">
                                <span>${escapeHtml(i18n.submitAnswer || 'Submit Answer')}</span>
                            </button>
                            <span class="submit-feedback-msg small"></span>
                        </div>
                    </form>
                `;
            }

            card.innerHTML = `
                <div class="card-header d-flex justify-content-between align-items-center flex-wrap gap-2">
                    <div class="d-flex align-items-center gap-2 flex-wrap">
                        <span class="question-number fw-bold text-light">${escapeHtml(i18n.question || 'Question')} ${idx + 1}</span>
                        <span class="points-badge">${q.points} ${escapeHtml(i18n.points || 'points')}</span>
                        ${typeBadge}
                    </div>
                    <div class="status-badge-container">${statusBadge}</div>
                </div>
                <div class="card-body">
                    <p class="fs-5 mb-4 text-light fw-medium">${escapeHtml(q.question_text)}</p>
                    <div class="question-body-dynamic">${cardBodyContent}</div>
                </div>
            `;

            return card;
        }

        function buildQuestionInputHTML(q) {
            if (q.question_type === 'free_text') {
                return `
                    <div class="mb-3">
                        <textarea name="answer" class="form-control" rows="3" placeholder="${escapeHtml(i18n.enterAnswerHere || 'Enter your answer here...')}" required></textarea>
                        ${q.requires_review ? `<small class="text-warning mt-2 d-block">ℹ️ ${escapeHtml(i18n.reviewNotice || 'This answer will be reviewed manually.')}</small>` : ''}
                    </div>
                `;
            } else if (q.question_type === 'multiple_select') {
                let optionsHtml = '';
                ['a', 'b', 'c', 'd'].forEach(function(optKey) {
                    const optVal = q['option_' + optKey];
                    if (optVal) {
                        optionsHtml += `
                            <label class="quiz-option">
                                <input type="checkbox" name="answer" value="${optKey}">
                                <span><strong>${optKey.toUpperCase()}.</strong> ${escapeHtml(optVal)}</span>
                            </label>
                        `;
                    }
                });
                return `
                    <div class="mb-3">${optionsHtml}
                        <small class="text-secondary mt-2 d-block">${escapeHtml(i18n.selectAllCorrect || 'Select all correct answers')}</small>
                    </div>
                `;
            } else {
                let optionsHtml = '';
                ['a', 'b', 'c', 'd'].forEach(function(optKey) {
                    const optVal = q['option_' + optKey];
                    if (optVal) {
                        optionsHtml += `
                            <label class="quiz-option">
                                <input type="radio" name="answer" value="${optKey}" required>
                                <span><strong>${optKey.toUpperCase()}.</strong> ${escapeHtml(optVal)}</span>
                            </label>
                        `;
                    }
                });
                return `<div class="mb-3">${optionsHtml}</div>`;
            }
        }

        function handleAnswerSubmit(form) {
            const questionId = parseInt(form.dataset.questionId, 10);
            const submitBtn = form.querySelector('.btn-submit-q');
            const feedbackMsg = form.querySelector('.submit-feedback-msg');

            let answerValue = null;
            const checkedInputs = form.querySelectorAll('input[name="answer"]:checked');
            const textarea = form.querySelector('textarea[name="answer"]');

            if (textarea) {
                answerValue = textarea.value.trim();
                if (!answerValue) return;
            } else if (checkedInputs.length > 0) {
                const values = Array.from(checkedInputs).map(function(i) { return i.value; });
                answerValue = values.join(',');
            } else {
                return;
            }

            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = i18n.submitting || 'Submitting...';
            }

            fetch('/api/quiz/submit_answer', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question_id: questionId, answer: answerValue })
            })
            .then(function(res) {
                if (!res.ok) {
                    return res.json().then(function(err) { throw new Error(err.error || 'Submission failed'); });
                }
                return res.json();
            })
            .then(function(resData) {
                // Update local question state
                const currentGroup = quizState.groups[quizState.currentGroupIndex];
                const targetQ = currentGroup ? currentGroup.questions.find(function(item) { return item.id === questionId; }) : null;
                if (targetQ) {
                    targetQ.answered = true;
                    targetQ.user_answer = resData.user_answer;
                    targetQ.is_correct = resData.is_correct;
                    targetQ.points_earned = resData.points_earned;
                    targetQ.is_reviewed = !resData.requires_review;
                }

                // Update team score display
                const teamScoreEl = document.getElementById('team-score-display');
                if (teamScoreEl && resData.team_score !== undefined) {
                    teamScoreEl.textContent = resData.team_score;
                }

                // Re-render card
                const card = form.closest('.question-card');
                if (card && targetQ) {
                    card.classList.add('is-answered');
                    const badgeContainer = card.querySelector('.status-badge-container');
                    if (badgeContainer) {
                        if (quizState.quiz.instant_feedback) {
                            if (resData.requires_review) {
                                badgeContainer.innerHTML = '<span class="badge bg-warning text-dark">' + escapeHtml(i18n.underReview || 'Under Review') + '</span>';
                            } else if (resData.is_correct) {
                                badgeContainer.innerHTML = '<span class="badge bg-success">' + escapeHtml(i18n.correct || 'Correct') + ' (+' + (resData.points_earned || 0) + ' pts)</span>';
                            } else {
                                badgeContainer.innerHTML = '<span class="badge bg-danger">' + escapeHtml(i18n.incorrect || 'Incorrect') + ' (0 pts)</span>';
                            }
                        } else {
                            badgeContainer.innerHTML = '<span class="badge bg-primary">' + escapeHtml(i18n.answerSaved || 'Answer saved') + '</span>';
                        }
                    }

                    const bodyDynamic = card.querySelector('.question-body-dynamic');
                    if (bodyDynamic) {
                        bodyDynamic.innerHTML = `
                            <div class="p-3 rounded bg-black bg-opacity-25 border border-secondary border-opacity-25">
                                <span class="text-secondary small d-block mb-1">${escapeHtml(i18n.yourAnswer || 'Your Answer')}:</span>
                                <strong class="text-light fs-6">${escapeHtml(targetQ.user_answer || '')}</strong>
                            </div>
                        `;
                    }
                }

                updateHeaderAndProgress();
            })
            .catch(function(err) {
                console.error(err);
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = i18n.submitAnswer || 'Submit Answer';
                }
                if (feedbackMsg) {
                    feedbackMsg.className = 'submit-feedback-msg small text-danger ms-2';
                    feedbackMsg.textContent = err.message;
                }
            });
        }

        function updateNavigationButtons() {
            const btnPrev = document.getElementById('btn-prev-group');
            const btnNext = document.getElementById('btn-next-group');
            const btnFinish = document.getElementById('btn-finish-quiz');

            const isFirst = quizState.currentGroupIndex === 0;
            const isLast = quizState.currentGroupIndex === quizState.groups.length - 1;

            if (isFirst) {
                btnPrev.style.display = 'none';
            } else {
                btnPrev.style.display = 'inline-block';
                // Check if returning to previous group is allowed
                const prevGroup = quizState.groups[quizState.currentGroupIndex - 1];
                if (prevGroup && prevGroup.allow_backtrack === false) {
                    btnPrev.disabled = true;
                    btnPrev.title = i18n.prevDisabledNotice || 'Backtracking disabled';
                    btnPrev.classList.add('opacity-50');
                } else {
                    btnPrev.disabled = false;
                    btnPrev.removeAttribute('title');
                    btnPrev.classList.remove('opacity-50');
                }
            }

            if (isLast) {
                btnNext.style.display = 'none';
                btnFinish.style.display = 'inline-block';
            } else {
                btnNext.style.display = 'inline-block';
                btnFinish.style.display = 'none';
            }
        }

        function updateHeaderAndProgress() {
            const groupStepEl = document.getElementById('group-step-indicator');
            const groupNameEl = document.getElementById('group-name-indicator');
            const progressText = document.getElementById('quiz-progress-text');
            const progressBar = document.getElementById('quiz-progress-bar');

            const currentGroup = quizState.groups[quizState.currentGroupIndex];
            if (groupStepEl && currentGroup) {
                groupStepEl.textContent = (i18n.group || 'Group') + ' ' + (quizState.currentGroupIndex + 1) + ' ' + (i18n.of || 'of') + ' ' + quizState.groups.length;
            }
            if (groupNameEl && currentGroup) {
                groupNameEl.textContent = currentGroup.name || '';
            }

            // Total answered count across all groups
            let totalAnswered = 0;
            quizState.groups.forEach(function(g) {
                g.questions.forEach(function(q) {
                    if (q.answered) totalAnswered++;
                });
            });

            const totalQuestions = quizState.allQuestions.length;
            if (progressText) {
                progressText.textContent = totalAnswered + '/' + totalQuestions + ' ' + (i18n.answered || 'answered');
            }
            if (progressBar && totalQuestions > 0) {
                const percent = Math.round((totalAnswered / totalQuestions) * 100);
                progressBar.style.width = percent + '%';
            }
        }

        // Navigation Button Listeners
        const btnPrev = document.getElementById('btn-prev-group');
        if (btnPrev) {
            btnPrev.addEventListener('click', function() {
                if (quizState.currentGroupIndex > 0) {
                    const prevGroup = quizState.groups[quizState.currentGroupIndex - 1];
                    if (prevGroup && prevGroup.allow_backtrack === false) return;

                    quizState.currentGroupIndex--;
                    saveProgressAndRender();
                }
            });
        }

        const btnNext = document.getElementById('btn-next-group');
        if (btnNext) {
            btnNext.addEventListener('click', function() {
                if (quizState.currentGroupIndex < quizState.groups.length - 1) {
                    quizState.currentGroupIndex++;
                    if (quizState.currentGroupIndex > quizState.highestGroupIndex) {
                        quizState.highestGroupIndex = quizState.currentGroupIndex;
                    }
                    saveProgressAndRender();
                }
            });
        }

        const btnFinish = document.getElementById('btn-finish-quiz');
        if (btnFinish) {
            btnFinish.addEventListener('click', function() {
                if (confirm(i18n.confirmFinish || 'Finish quiz?')) {
                    btnFinish.disabled = true;
                    fetch('/api/events/' + eventId + '/complete', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' }
                    })
                    .then(function(res) { return res.json(); })
                    .then(function() {
                        window.location.href = window.QUIZ_CONFIG.resultsUrl;
                    })
                    .catch(function(err) {
                        console.error('Error finishing quiz:', err);
                        window.location.href = window.QUIZ_CONFIG.resultsUrl;
                    });
                }
            });
        }

        function saveProgressAndRender() {
            fetch('/api/events/' + eventId + '/update_progress', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ group_index: quizState.currentGroupIndex })
            }).catch(function(err) { console.error('Error saving progress:', err); });

            renderCurrentGroup();
            updateNavigationButtons();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    }

    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    // Expose utility functions to window
    window.QuizApp = {
        updateProgressBar: updateProgressBar
    };
})();
