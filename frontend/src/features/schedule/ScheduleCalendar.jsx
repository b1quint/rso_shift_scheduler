import { useState, useEffect } from 'react';
import api from '../../services/api';
import { staffService, shiftService } from '../../services';
import './ScheduleCalendar.css';

const ScheduleCalendar = () => {
  const [staff, setStaff] = useState([]);
  const [shifts, setShifts] = useState([]);
  const [teams, setTeams] = useState([]);
  const [selectedTeam, setSelectedTeam] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [hoveredColumn, setHoveredColumn] = useState(null);
  
  // Initialize with current week (today to 6 days later)
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const oneWeekLater = new Date(today);
  oneWeekLater.setDate(today.getDate() + 6);
  
  const [startDate, setStartDate] = useState(today);
  const [endDate, setEndDate] = useState(oneWeekLater);
  const [tempStartDate, setTempStartDate] = useState(today.toISOString().split('T')[0]);
  const [tempEndDate, setTempEndDate] = useState(oneWeekLater.toISOString().split('T')[0]);

  // Calculate the dates between start and end
  const getDateRange = (start, end) => {
    const dates = [];
    const currentDate = new Date(start);
    const endDate = new Date(end);
    
    while (currentDate <= endDate) {
      dates.push(new Date(currentDate));
      currentDate.setDate(currentDate.getDate() + 1);
    }
    return dates;
  };

  const displayDates = getDateRange(startDate, endDate);

  // Handle date range update
  const handleUpdateDateRange = () => {
    const start = new Date(tempStartDate);
    const end = new Date(tempEndDate);
    
    if (start > end) {
      alert('Start date must be before or equal to end date');
      return;
    }
    
    start.setHours(0, 0, 0, 0);
    end.setHours(0, 0, 0, 0);
    
    setStartDate(start);
    setEndDate(end);
  };

  // Quick preset buttons
  const setThisWeek = () => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const weekEnd = new Date(today);
    weekEnd.setDate(today.getDate() + 6);
    
    setTempStartDate(today.toISOString().split('T')[0]);
    setTempEndDate(weekEnd.toISOString().split('T')[0]);
    setStartDate(today);
    setEndDate(weekEnd);
  };

  const setThisMonth = () => {
    const today = new Date();
    const monthStart = new Date(today.getFullYear(), today.getMonth(), 1);
    const monthEnd = new Date(today.getFullYear(), today.getMonth() + 1, 0);
    
    setTempStartDate(monthStart.toISOString().split('T')[0]);
    setTempEndDate(monthEnd.toISOString().split('T')[0]);
    setStartDate(monthStart);
    setEndDate(monthEnd);
  };

  // Fetch teams on mount
  useEffect(() => {
    const fetchTeams = async () => {
      try {
        const response = await api.get('/staff/teams/');
        setTeams(response.data.results || response.data);
      } catch (err) {
        console.error('Error fetching teams:', err);
      }
    };
    fetchTeams();
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch staff members (filtered by team if selected)
        const staffParams = selectedTeam ? { team: selectedTeam } : {};
        const staffResponse = await staffService.getAll(staffParams);
        setStaff(staffResponse.data.results || staffResponse.data);

        // Fetch shifts for the selected date range
        const startDateStr = startDate.toISOString().split('T')[0];
        const endDateStr = endDate.toISOString().split('T')[0];
        
        const shiftsResponse = await shiftService.getAll({
          start_time__gte: startDateStr,
          start_time__lte: endDateStr
        });
        setShifts(shiftsResponse.data.results || shiftsResponse.data);

        setLoading(false);
      } catch (err) {
        console.error('Error fetching schedule data:', err);
        setError('Failed to load schedule data');
        setLoading(false);
      }
    };

    fetchData();
  }, [startDate, endDate, selectedTeam]);

  // Find shifts for a specific staff member on a specific date
  const getShiftsForStaffOnDate = (staffId, date) => {
    const dateStr = date.toISOString().split('T')[0];
    
    return shifts.filter(shift => {
      const shiftDate = new Date(shift.start_time).toISOString().split('T')[0];
      return shift.assigned_staff === staffId && shiftDate === dateStr;
    });
  };

  // Format date parts for column headers
  const getMonthName = (date) => {
    return date.toLocaleDateString('en-US', { month: 'long' });
  };

  const getDayNumber = (date) => {
    return date.getDate();
  };

  const getDayOfWeek = (date) => {
    return date.toLocaleDateString('en-US', { weekday: 'short' });
  };

  // Calculate month spans for the header
  const getMonthSpans = () => {
    const spans = [];
    let currentMonth = null;
    let currentYear = null;
    let span = 0;

    displayDates.forEach((date, index) => {
      const month = date.getMonth();
      const year = date.getFullYear();
      
      if (currentMonth === month && currentYear === year) {
        span++;
      } else {
        if (currentMonth !== null) {
          spans.push({ month: currentMonth, year: currentYear, span });
        }
        currentMonth = month;
        currentYear = year;
        span = 1;
      }
      
      if (index === displayDates.length - 1) {
        spans.push({ month: currentMonth, year: currentYear, span });
      }
    });

    return spans;
  };

  const monthSpans = getMonthSpans();

  // Format month name with year
  const formatMonthYear = (monthIndex, year) => {
    const date = new Date(year, monthIndex, 1);
    return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  };

  // Check if date is today
  const isToday = (date) => {
    const today = new Date();
    return date.toDateString() === today.toDateString();
  };

  // Check if date is weekend (Saturday = 6, Sunday = 0)
  const isWeekend = (date) => {
    const day = date.getDay();
    return day === 0 || day === 6;
  };

  // Get shift type badge class
  const getShiftTypeBadge = (shiftType) => {
    const badges = {
      'night': 'shift-badge-night',
      'day': 'shift-badge-day',
      'twilight': 'shift-badge-twilight',
      'on_call': 'shift-badge-oncall'
    };
    return badges[shiftType] || 'shift-badge-default';
  };

  // Format shift time range
  const formatShiftTime = (startTime, endTime) => {
    const start = new Date(startTime);
    const end = new Date(endTime);
    return `${start.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })} - ${end.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })}`;
  };

  if (loading) {
    return <div className="schedule-loading">Loading schedule...</div>;
  }

  if (error) {
    return <div className="schedule-error">{error}</div>;
  }

  return (
    <div className="schedule-calendar">
      <div className="schedule-header">
        <h1>Staff Schedule</h1>
        <div className="date-range-controls">
          <div className="date-inputs">
            <div className="date-input-group">
              <label htmlFor="team-filter">Filter by Team</label>
              <select
                id="team-filter"
                value={selectedTeam}
                onChange={(e) => setSelectedTeam(e.target.value)}
                className="date-input"
              >
                <option value="">All Teams</option>
                {teams.map((team) => (
                  <option key={team.id} value={team.id}>
                    {team.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="date-input-group">
              <label htmlFor="start-date">Start Date</label>
              <input
                id="start-date"
                type="date"
                value={tempStartDate}
                onChange={(e) => setTempStartDate(e.target.value)}
                className="date-input"
              />
            </div>
            <div className="date-input-group">
              <label htmlFor="end-date">End Date</label>
              <input
                id="end-date"
                type="date"
                value={tempEndDate}
                onChange={(e) => setTempEndDate(e.target.value)}
                className="date-input"
              />
            </div>
            <button onClick={handleUpdateDateRange} className="update-button">
              Update View
            </button>
          </div>
          <div className="preset-buttons">
            <button onClick={setThisWeek} className="preset-button">
              This Week
            </button>
            <button onClick={setThisMonth} className="preset-button">
              This Month
            </button>
          </div>
        </div>
      </div>

      <div className="schedule-table-container">
        <table className="schedule-table">
          <thead>
            <tr className="header-row-month">
              <th className="staff-column-header" rowSpan="3">Staff Member</th>
              {monthSpans.map((monthSpan, index) => (
                <th 
                  key={index} 
                  colSpan={monthSpan.span}
                  className="date-column-header month-header"
                >
                  {formatMonthYear(monthSpan.month, monthSpan.year)}
                </th>
              ))}
            </tr>
            <tr className="header-row-date">
              {displayDates.map((date, index) => (
                <th 
                  key={index} 
                  className={`date-column-header date-number ${isToday(date) ? 'today' : ''} ${isWeekend(date) ? 'weekend' : ''} ${hoveredColumn === index ? 'hovered' : ''}`}
                  onMouseEnter={() => setHoveredColumn(index)}
                  onMouseLeave={() => setHoveredColumn(null)}
                >
                  {getDayNumber(date)}
                </th>
              ))}
            </tr>
            <tr className="header-row-weekday">
              {displayDates.map((date, index) => (
                <th 
                  key={index} 
                  className={`date-column-header weekday-header ${isToday(date) ? 'today' : ''} ${isWeekend(date) ? 'weekend' : ''} ${hoveredColumn === index ? 'hovered' : ''}`}
                  onMouseEnter={() => setHoveredColumn(index)}
                  onMouseLeave={() => setHoveredColumn(null)}
                >
                  {getDayOfWeek(date)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {staff.map((staffMember) => (
              <tr key={staffMember.id}>
                <td className="staff-cell">
                  <div className="staff-info">
                    <div className="staff-name">{staffMember.full_name}</div>
                    <div className="staff-role">
                      {staffMember.team_code && (
                        <span className="team-badge">{staffMember.team_code}</span>
                      )}
                      {staffMember.role_display}
                    </div>
                  </div>
                </td>
                {displayDates.map((date, dateIndex) => {
                  const dayShifts = getShiftsForStaffOnDate(staffMember.id, date);
                  
                  return (
                    <td 
                      key={dateIndex} 
                      className={`shift-cell ${isToday(date) ? 'today' : ''} ${isWeekend(date) ? 'weekend' : ''} ${hoveredColumn === dateIndex ? 'hovered' : ''} ${dayShifts.length > 0 ? 'has-shifts' : 'empty'}`}
                      onMouseEnter={() => setHoveredColumn(dateIndex)}
                      onMouseLeave={() => setHoveredColumn(null)}
                    >
                      {dayShifts.length > 0 ? (
                        <div className="shifts-compact">
                          {dayShifts.map((shift, shiftIndex) => {
                            const shiftCode = shift.shift_code || '?';
                            const shiftNumber = dayShifts.length > 1 ? shiftIndex + 1 : '';
                            const shiftColor = shift.shift_color || '#6b7280';
                            return (
                              <span 
                                key={shift.id} 
                                className="shift-code"
                                style={{ backgroundColor: shiftColor, color: 'white' }}
                                title={`${shift.shift_name}\n${formatShiftTime(shift.start_time, shift.end_time)}\n${shift.telescope_name || 'No telescope'}`}
                              >
                                {shiftCode}{shiftNumber}
                              </span>
                            );
                          })}
                        </div>
                      ) : (
                        <div className="no-shift">—</div>
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {staff.length === 0 && (
        <div className="no-data">
          No staff members found. Please add staff members to see the schedule.
        </div>
      )}
    </div>
  );
};

export default ScheduleCalendar;
