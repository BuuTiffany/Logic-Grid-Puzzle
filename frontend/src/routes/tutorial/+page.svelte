<div class="bg-grid"></div>

<main class="page-shell">
    <section class="intro">
        <span class="label-sm">Tutorial</span>
        <h1>How to Play</h1>
        <p>Read the clues. Fill the grid. Every row needs one value in each position. The puzzle is won when every value matches the hidden solution.</p>
    </section>

    <section class="steps">
        <div class="step-card">
            <span class="step-num">01</span>
            <h2>Pick a puzzle</h2>
            <p>Choose a grid size and difficulty. Bigger grids have more categories or positions. Harder puzzles give you less direct information.</p>
        </div>

        <div class="step-card">
            <span class="step-num">02</span>
            <h2>Read each clue</h2>
            <p>A clue tells you where a value belongs or how two values relate. Use every clue. Do not guess unless you are testing a possibility.</p>
        </div>

        <div class="step-card">
            <span class="step-num">03</span>
            <h2>Place values</h2>
            <p>Drag values into cells. Each position can only use one value from each category. If a value creates a contradiction, move it.</p>
        </div>

        <div class="step-card">
            <span class="step-num">04</span>
            <h2>Use hints if stuck</h2>
            <p>A hint reveals one correct cell. It helps you keep moving, but it reduces the challenge. Use it only when the board is blocked.</p>
        </div>

        <div class="step-card">
            <span class="step-num">05</span>
            <h2>Check the solution</h2>
            <p>Press Check Solution when the grid is filled. If it is wrong, inspect the clues again and fix the contradiction.</p>
        </div>

        <div class="step-card">
            <span class="step-num">06</span>
            <h2>Win cleanly</h2>
            <p>You win when every category line is complete and the answer passes validation. Logged-in users save their score automatically.</p>
        </div>
    </section>
</main>

<style>
    .page-shell {
        position: relative;
        z-index: 1;
        max-width: 980px;
        margin: 0 auto;
        padding: 4rem 2rem;
        display: flex;
        flex-direction: column;
        gap: 2rem;
    }

    .intro {
        max-width: 680px;
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
    .step-card p {
        color: var(--text-dim);
        font-size: 0.86rem;
    }

    .steps {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 1rem;
    }

    .step-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 1.25rem;
        display: flex;
        flex-direction: column;
        gap: 0.55rem;
    }

    .step-num {
        font-size: 0.62rem;
        letter-spacing: 0.18em;
        color: var(--gold);
    }

    h2 {
        color: var(--text-mid);
        font-size: 1.1rem;
    }

    @media (max-width: 700px) {
        .steps {
            grid-template-columns: 1fr;
        }

        h1 {
            font-size: 2.4rem;
        }
    }
</style>
