import "./Header.css";

function Header() {
  return (
    <header className="header">
      <h2 className="logo">Git Analytics</h2>

      <nav className="nav">
        <a href="#">Home</a>
        <a href="#">Contributions</a>
      </nav>
    </header>
  );
}

export default Header;