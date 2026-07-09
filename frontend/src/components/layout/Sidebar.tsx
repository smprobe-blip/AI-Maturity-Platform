import { NavLink } from 'react-router-dom';
import { LogOut } from 'lucide-react';
import { useAuth } from '@/auth/KeycloakProvider';
import { cn } from '@/utils/cn';
import { menuGroups } from './menuConfig';

export function Sidebar() {
  const { user, logout } = useAuth();

  // Фильтрация пунктов меню по ролям
  const filterItems = (items: typeof menuGroups[0]['items']) => {
    return items.filter(item => {
      if (!item.requiredRole) return true;
      return user?.roles?.includes(item.requiredRole);
    });
  };

  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col h-screen sticky top-0 shadow-sm">
      {/* Logo */}
      <div className="px-6 py-5 border-b border-gray-200 bg-gradient-to-r from-primary-50 to-white">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-primary-600 to-primary-700 rounded-xl flex items-center justify-center text-white font-bold shadow-md">
            AI
          </div>
          <div>
            <div className="font-bold text-gray-900 text-base">AI Maturity</div>
            <div className="text-xs text-gray-500">Admin Panel</div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-6 overflow-y-auto">
        {menuGroups.map((group) => {
          const filteredItems = filterItems(group.items);
          if (filteredItems.length === 0) return null;

          return (
            <div key={group.title}>
              <div className="px-3 mb-2 text-xs font-semibold text-gray-400 uppercase tracking-wider">
                {group.title}
              </div>
              <div className="space-y-1">
                {filteredItems.map((item) => (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    end={item.end}
                    className={({ isActive }) =>
                      cn(
                        'group relative flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200',
                        isActive
                          ? 'bg-primary-50 text-primary-700 shadow-sm'
                          : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900 hover:translate-x-1'
                      )
                    }
                  >
                    {({ isActive }) => (
                      <>
                        {/* Active indicator */}
                        {isActive && (
                          <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-primary-600 rounded-r-full" />
                        )}
                        
                        {/* Icon */}
                        <item.icon 
                          className={cn(
                            'w-5 h-5 transition-transform duration-200',
                            isActive ? 'text-primary-600' : 'text-gray-500 group-hover:text-gray-700'
                          )} 
                        />
                        
                        {/* Label */}
                        <span className="flex-1">{item.label}</span>
                      </>
                    )}
                  </NavLink>
                ))}
              </div>
            </div>
          );
        })}
      </nav>

      {/* User section */}
      <div className="border-t border-gray-200 p-4 bg-gradient-to-t from-gray-50 to-white">
        <div className="flex items-center gap-3 mb-3 p-2 rounded-lg hover:bg-white transition-colors">
          <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-full flex items-center justify-center text-white font-semibold shadow-md">
            {user?.name?.[0]?.toUpperCase() || 'U'}
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-sm font-semibold text-gray-900 truncate">
              {user?.name || 'User'}
            </div>
            <div className="text-xs text-gray-500 truncate">{user?.email}</div>
          </div>
        </div>
        <button
          onClick={logout}
          className="w-full flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm text-gray-700 hover:bg-red-50 hover:text-red-700 transition-all duration-200 group"
        >
          <LogOut className="w-4 h-4 transition-transform duration-200 group-hover:-translate-x-1" />
          <span className="font-medium">Выйти</span>
        </button>
      </div>
    </aside>
  );
}
