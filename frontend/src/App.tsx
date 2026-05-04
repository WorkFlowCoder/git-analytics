import './App.css'
import MainLayout from './layouts/MainLayout';
import Home from './pages/Home';
import RepoPage from "./pages/RepoPage";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import RepositoriesPage from './pages/RepositoriesPage';


function App() {
  return (
    <MainLayout>
      <BrowserRouter>
        <Routes>
          <Route path="/repo/:id" element={<RepoPage/>} />
          <Route path="/repo" element={<RepositoriesPage />} />
          <Route path="/" element={<Home />} />
        </Routes>
      </BrowserRouter>
    </MainLayout>
  );
}

export default App;
