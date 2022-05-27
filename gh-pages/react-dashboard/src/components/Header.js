export default function Header() {
  return (
    <header>
      <h2>React Github Page Spike</h2>
      <h4>Simple React Proof-of-Concept v0.2</h4>
      <p>You are running this application in <b>{process.env.NODE_ENV}</b> mode.</p>
    </header>
  )
}
