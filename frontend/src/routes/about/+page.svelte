<div class="bg-grid"></div>

<main class="page-shell">
    <section class="intro">
        <span class="label-sm">About</span>
        <h1>Logic Grid Puzzle</h1>
        <p>This capstone project is a web application for generated logic grid puzzles. It combines puzzle generation, validation, hints, user accounts, profiles, and leaderboards.</p>
    </section>

    <section class="content-grid">
        <article class="info-card wide">
            <h2>Capstone Summary</h2>
            <p>The project applies frontend development, backend development, database design, authentication, and algorithmic puzzle generation. The main technical challenge is producing playable logic puzzles, storing them, serving them through an API, and validating user solutions without exposing the answer.</p>
        </article>

        <article class="info-card">
            <h2>Logic Puzzle Mechanics</h2>
            <p>The game generates category-based puzzles with different grid sizes and difficulties. Clues describe relationships between values. Players place values in the grid, request hints when needed, and submit the completed board for validation.</p>
        </article>

        <article class="info-card">
            <h2>Purpose</h2>
            <p>The purpose is to make logic grid puzzles easier to access, replay, and compare. The app gives users generated puzzles instead of a fixed worksheet and records solve performance for logged-in players.</p>
        </article>

        <article class="info-card">
            <h2>Audience</h2>
            <p>The target audience is people who like deduction puzzles, students practicing reasoning, and users who want short puzzle sessions with saved progress and rankings.</p>
        </article>

        <article class="info-card">
            <h2>Vision Statement</h2>
            <p>The vision is a clean puzzle site where users can generate a logic grid, solve it, receive help only when needed, and compare results with other players.</p>
        </article>

        <article class="info-card">
            <h2>Elevator Pitch</h2>
            <p>Logic Grid Puzzle turns classic deduction puzzles into an interactive web app. Pick a size, choose a difficulty, solve the board, and compete on time.</p>
        </article>

        <article class="info-card">
            <h2>Scope</h2>
            <p>The scope includes generated puzzles, multiple grid sizes, difficulty settings, hints, solution checking, guest play, Django authentication, Google sign-in, profiles, and leaderboard tracking.</p>
        </article>

        <article class="info-card">
            <h2>Objectives</h2>
            <p>The project objectives are to deliver a working logic puzzle web application, develop a collaborative workflow, practice project management, and build a full-stack system that is usable beyond a static prototype.</p>
        </article>
    </section>

    <a class="repo-btn" href="https://github.com/BuuTiffany/Logic-Grid-Puzzle" target="_blank" rel="noreferrer">
        github repository of our project
    </a>
</main>

<style>
    .page-shell {
        position: relative;
        z-index: 1;
        max-width: 1040px;
        margin: 0 auto;
        padding: 4rem 2rem;
        display: flex;
        flex-direction: column;
        gap: 2rem;
    }

    .intro {
        max-width: 760px;
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
    }

    h1 {
        font-size: 3rem;
        color: var(--text);
        line-height: 1;
    }

    .intro p,
    .info-card p {
        color: var(--text-dim);
        font-size: 0.86rem;
    }

    .content-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 1rem;
    }

    .info-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 1.25rem;
        display: flex;
        flex-direction: column;
        gap: 0.65rem;
    }

    .wide {
        grid-column: 1 / -1;
    }

    h2 {
        color: var(--text-mid);
        font-size: 1.1rem;
    }

    .repo-btn {
        align-self: flex-start;
        background: var(--gold);
        border-radius: var(--radius-md);
        color: var(--bg);
        font-family: var(--font-mono);
        font-size: 0.82rem;
        font-weight: 500;
        letter-spacing: 0.05em;
        padding: 0.8rem 1.2rem;
        text-decoration: none;
        transition: filter 0.15s, transform 0.15s;
    }

    .repo-btn:hover {
        filter: brightness(1.1);
        transform: translateY(-1px);
    }

    @media (max-width: 720px) {
        .content-grid {
            grid-template-columns: 1fr;
        }

        .wide {
            grid-column: auto;
        }

        h1 {
            font-size: 2.4rem;
        }
    }
</style>
