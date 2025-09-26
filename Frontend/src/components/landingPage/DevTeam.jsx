import React from 'react';
import { WavyBackground } from '../ui/wavy-background';

import avatarSaurabh from '../../assets/team/avatar-saurabh.svg';
import avatarEka from '../../assets/team/avatar-eka.svg';
import avatarMaya from '../../assets/team/avatar-maya.svg';
import avatarLiam from '../../assets/team/avatar-liam.svg';
import avatarX from '../../assets/team/avatar-x.svg';

const team = [
  { name: 'Saurabh', role: 'Full-stack Engineer', twitter: 'saurabh', image: avatarSaurabh },
  { name: 'Eka', role: 'Blockchain Engineer', twitter: 'eka', image: avatarEka },
  { name: 'Maya', role: 'Product Designer', twitter: 'maya', image: avatarMaya },
  { name: 'Liam', role: 'DevOps', twitter: 'liam', image: avatarLiam },
  { name: 'X', role: 'Contributor', github: 'usernameX', linkedin: 'usernameX', image: avatarX },
];

function DevTeam() {
  const getSocialIcon = (platform) => {
    const iconClass = "w-4 h-4 text-white/80 group-hover:text-white transition-colors";
    
    switch (platform) {
      case 'github':
        return (
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className={iconClass}>
            <path d="M12 .5C5.73.5.75 5.48.75 11.75c0 4.93 3.19 9.1 7.61 10.57.56.1.77-.24.77-.54 0-.26-.01-1.14-.02-2.07-3.09.67-3.74-1.49-3.74-1.49-.5-1.28-1.22-1.62-1.22-1.62-.99-.68.08-.67.08-.67 1.1.08 1.68 1.12 1.68 1.12.98 1.67 2.57 1.19 3.2.91.1-.71.38-1.19.69-1.47-2.47-.28-5.07-1.23-5.07-5.47 0-1.21.43-2.2 1.14-2.98-.11-.29-.5-1.45.11-3.02 0 0 .93-.3 3.05 1.13.88-.24 1.82-.36 2.76-.36.94 0 1.88.12 2.76.36 2.12-1.43 3.05-1.13 3.05-1.13.61 1.57.22 2.73.11 3.02.71.78 1.14 1.77 1.14 2.98 0 4.25-2.61 5.19-5.09 5.46.39.34.73 1.01.73 2.04 0 1.47-.01 2.66-.01 3.02 0 .3.21.65.78.54C20.07 20.85 23.25 16.68 23.25 11.75 23.25 5.48 18.27.5 12 .5z" />
          </svg>
        );
      case 'twitter':
        return (
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className={iconClass}>
            <path d="M22.46 6c-.77.35-1.6.58-2.46.69.89-.53 1.57-1.37 1.88-2.37-.84.5-1.77.86-2.76 1.06A4.15 4.15 0 0015.5 4c-2.3 0-4.16 1.86-4.16 4.16 0 .33.04.65.11.96C7.72 8.95 4.1 6.98 1.67 4.15c-.36.6-.57 1.3-.57 2.04 0 1.41.72 2.66 1.82 3.39-.67-.02-1.3-.21-1.85-.51v.05c0 1.96 1.4 3.6 3.25 3.97-.34.09-.7.14-1.07.14-.26 0-.52-.03-.77-.07.52 1.63 2.03 2.82 3.82 2.85A8.34 8.34 0 01.98 19.54 11.78 11.78 0 006.29 21c7.55 0 11.68-6.25 11.68-11.67v-.53A8.2 8.2 0 0022.46 6z" />
          </svg>
        );
      case 'linkedin':
        return (
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className={iconClass}>
            <path d="M4.98 3.5C4.98 4.88 3.88 6 2.5 6S0 4.88 0 3.5 1.1 1 2.5 1 4.98 2.12 4.98 3.5zM.5 8.5h4v13h-4v-13zM9 8.5h3.8v1.73h.05c.53-1 1.82-2.05 3.75-2.05 4.01 0 4.75 2.64 4.75 6.07V21.5h-4v-5.7c0-1.36-.03-3.12-1.9-3.12-1.9 0-2.19 1.48-2.19 3v5.82H9v-13z"/>
          </svg>
        );
      default:
        return null;
    }
  };

  const getSocialLinks = (member) => {
    const links = [];
    
    if (member.github) {
      links.push({
        platform: 'github',
        url: `https://github.com/${member.github}`,
        label: 'GitHub Profile'
      });
    }
    
    if (member.twitter) {
      links.push({
        platform: 'twitter',
        url: `https://x.com/${member.twitter}`,
        label: 'Twitter Profile'
      });
    }
    
    if (member.linkedin) {
      links.push({
        platform: 'linkedin',
        url: `https://linkedin.com/in/${member.linkedin}`,
        label: 'LinkedIn Profile'
      });
    }
    
    return links;
  };

  return (
    <WavyBackground 
      fullScreen={false} 
      containerClassName="w-full py-16 bg-gradient-to-b from-black/80 to-black/90 relative" 
      className="max-w-7xl mx-auto pb-40"
    >
      <section id="dev-team" className="w-full">
        <div className="max-w-6xl mx-auto  relative z-20">
          <div className="text-center mb-4">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Meet the Team
            </h2>
            <p className="text-lg text-white/80 max-w-2xl mx-auto leading-relaxed">
              The passionate developers, designers, and engineers building the future of EchoNet.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
            {team.map((member, idx) => {
              const socialLinks = getSocialLinks(member);
              
              return (
                <div 
                  key={idx} 
                  className="group relative bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-6 hover:bg-white/10 hover:border-white/20 transition-all duration-300 hover:transform hover:-translate-y-2 hover:shadow-2xl"
                >
                  {/* Avatar */}
                  <div className="flex justify-center mb-4">
                    <div className="relative">
                      <img
                        src={member.image}
                        alt={`${member.name} - ${member.role}`}
                        className="w-20 h-20 rounded-2xl object-cover border-2 border-white/20 group-hover:border-white/40 transition-all duration-300"
                      />
                      <div className="absolute inset-0 rounded-2xl bg-gradient-to-t from-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                    </div>
                  </div>

                  {/* Content */}
                  <div className="text-center mb-4">
                    <h3 className="text-xl font-semibold text-white mb-1 group-hover:text-white/90 transition-colors">
                      {member.name}
                    </h3>
                    <p className="text-white/70 text-sm font-medium">
                      {member.role}
                    </p>
                  </div>

                  {/* Social Links */}
                  {socialLinks.length > 0 && (
                    <div className="flex justify-center gap-3">
                      {socialLinks.map((link, linkIdx) => (
                        <a
                          key={linkIdx}
                          href={link.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          aria-label={link.label}
                          className="group/icon w-8 h-8 rounded-lg bg-white/5 hover:bg-white/15 flex items-center justify-center transition-all duration-200 hover:scale-110"
                        >
                          {getSocialIcon(link.platform)}
                        </a>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </section>
    </WavyBackground>
  );
}

export default DevTeam;
