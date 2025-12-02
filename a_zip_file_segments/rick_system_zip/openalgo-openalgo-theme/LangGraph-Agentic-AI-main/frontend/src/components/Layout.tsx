import { Outlet } from 'react-router-dom';
import { Navbar } from './Navbar';
import { Header } from './Header';
import { motion } from 'framer-motion';

export function Layout() {
  return (
    <div className="flex h-screen overflow-hidden bg-dark-900">
      <Navbar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <Header />
        <motion.main
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
          className="flex-1 overflow-y-auto p-4 bg-dark-800"
        >
          <Outlet />
        </motion.main>
      </div>
    </div>
  );
}
